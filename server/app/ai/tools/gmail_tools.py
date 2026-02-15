import base64
import httpx
import json
from typing import Optional, Annotated, List, Dict, Any
from pydantic.json_schema import SkipJsonSchema
from uuid import UUID

from langchain_core.tools import tool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.integrations.google import validate_google_capability


GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


# SCHEMAS
from pydantic import BaseModel, Field, EmailStr

class SendGmailSchema(BaseModel):
    to: EmailStr = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class FetchGmailSchema(BaseModel):
    max_results: int = Field(default=5, description="Number of recent emails to fetch")
    query: Optional[str] = Field(default=None, description="Gmail search query (e.g. 'from:boss', 'invoice')")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class ReadGmailMessageSchema(BaseModel):
    message_id: str = Field(description="The Google message ID to read")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class VerifyDeliverySchema(BaseModel):
    recipient: str = Field(description="The recipient email address to check for bounces")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None


# SEND EMAIL TOOL
@tool(args_schema=SendGmailSchema)
async def send_gmail(
    session: AsyncSession,
    user_id: UUID,
    to: str,
    subject: str,
    body: str,
) -> Dict[str, Any]:
    """
    Send an email using the user's Gmail account.
    Requires Gmail send permission.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="gmail.send",
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    message_text = f"To: {to}\nSubject: {subject}\n\n{body}"

    encoded_message = base64.urlsafe_b64encode(
        message_text.encode("utf-8")
    ).decode("utf-8")

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{GMAIL_API_BASE}/users/me/messages/send",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "raw": encoded_message
            },
        )

    if resp.status_code >= 400:
        try:
            error_data = resp.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown Gmail API error.")
        except:
            error_msg = "Failed to send email. Gmail API error."
        return {"status": "error", "message": f"Gmail Error: {error_msg}"}

    # PROACTIVE BOUNCE CHECK
    # Wait a few seconds for Google to process and potentially bounce the message
    import asyncio
    await asyncio.sleep(3)
    
    # Check for immediate bounces
    bounce_query = f"from:mailer-daemon {to}"
    async with httpx.AsyncClient(timeout=10) as client:
        bounce_resp = await client.get(
            f"{GMAIL_API_BASE}/users/me/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"q": bounce_query, "maxResults": 1}
        )
        
        if bounce_resp.status_code == 200:
            bounce_data = bounce_resp.json()
            if bounce_data.get("resultSizeEstimate", 0) > 0:
                return {
                    "status": "error", 
                    "message": f"Message DISPATCHED but immediately FAILED. Google reports that the address '{to}' could not be found. Please check the spelling."
                }

    return {"status": "success", "message": f"Email successfully delivered to {to}."}

# VERIFY DELIVERY TOOL
@tool(args_schema=VerifyDeliverySchema)
async def verify_delivery(
    session: AsyncSession,
    user_id: UUID,
    recipient: str,
) -> Dict[str, Any]:
    """
    Check if an email sent to a specific recipient has failed/bounced back. 
    Use this if you are unsure if an email was actually delivered.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="gmail.readonly",
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]
    
    # Search for bounces (from mailer-daemon mentioning the recipient)
    query = f"from:mailer-daemon {recipient}"
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GMAIL_API_BASE}/users/me/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"q": query, "maxResults": 1}
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": "Failed to check delivery status."}

    data = resp.json()
    if data.get("resultSizeEstimate", 0) > 0:
        return {
            "status": "failed",
            "message": f"Delivery FAILED. Found a bounce-back message in the inbox for {recipient}. The address probably doesn't exist."
        }

    return {
        "status": "success",
        "message": f"No bounce-back found for {recipient} yet. It likely reached the destination."
    }



# FETCH RECENT EMAILS
@tool(args_schema=FetchGmailSchema)
async def fetch_recent_gmail(
    session: AsyncSession,
    user_id: UUID,
    max_results: int = 5,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch and read full email contents from Gmail.
    Can search by sender or content using the query parameter.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="gmail.readonly",
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]
    
    # Default to fetching from Inbox unless a specific query is provided
    search_query = query if query else "label:INBOX"
    
    params = {
        "maxResults": max_results,
        "q": search_query
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GMAIL_API_BASE}/users/me/messages",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            params=params,
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": "Failed to fetch emails. Access might be restricted."}

    data = resp.json()
    messages = data.get("messages", [])
    if not messages:
        return {"status": "success", "count": 0, "emails": []}

    emails = []

    async with httpx.AsyncClient(timeout=15) as client:
        for msg in messages:
            msg_id = msg["id"]
            detail_resp = await client.get(
                f"{GMAIL_API_BASE}/users/me/messages/{msg_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if detail_resp.status_code >= 400:
                continue

            detail = detail_resp.json()
            payload = detail.get("payload", {})
            headers = payload.get("headers", [])
            
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "(Unknown Sender)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(Unknown Date)")
            
            body_text = _extract_body(payload)
            
            emails.append({
                "id": msg_id,
                "from": sender,
                "date": date,
                "subject": subject,
                "body": body_text
            })

    return {
        "status": "success",
        "count": len(emails),
        "emails": emails
    }


# READ SPECIFIC EMAIL
@tool(args_schema=ReadGmailMessageSchema)
async def read_gmail_message(
    session: AsyncSession,
    user_id: UUID,
    message_id: str,
) -> Dict[str, Any]:
    """
    Fetch the full body of a specific Gmail message by its ID.
    User can get IDs from fetch_recent_gmail.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="gmail.readonly",
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GMAIL_API_BASE}/users/me/messages/{message_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": "Failed to fetch email body."}

    detail = resp.json()
    payload = detail.get("payload", {})
    body_text = _extract_body(payload)

    return {
        "status": "success",
        "id": message_id,
        "subject": next((h["value"] for h in payload.get("headers", []) if h["name"] == "Subject"), "(No Subject)"),
        "body": body_text
    }

def _extract_body(payload: dict) -> str:
    """Helper to extract full body content from Gmail payload, handling multipart and HTML."""
    
    def decode(data):
        return base64.urlsafe_b64decode(data).decode("utf-8")

    def walk_parts(parts_list):
        plain_text = ""
        html_text = ""
        
        for part in parts_list:
            mime = part.get("mimeType")
            body = part.get("body", {})
            data = body.get("data")
            
            if mime == "text/plain" and data:
                plain_text += decode(data)
            elif mime == "text/html" and data:
                html_text += decode(data)
            
            # Recursive check for nested parts
            if "parts" in part:
                p, h = walk_parts(part["parts"])
                plain_text += p
                html_text += h
        
        return plain_text, html_text

    # 1. Check root level body
    root_body = payload.get("body", {}).get("data")
    if root_body:
        return decode(root_body)

    # 2. Walk all parts to collect content
    parts = payload.get("parts", [])
    all_plain, all_html = walk_parts(parts)

    # If both exist, choose the most comprehensive one (usually HTML for styled emails)
    if all_html and len(all_html) > len(all_plain) * 1.5:
        use_html = True
    elif not all_plain and all_html:
        use_html = True
    else:
        use_html = False

    if use_html:
        # Improved HTML to text conversion to preserve structure for the LLM
        import re
        text = all_html
        # 1. Remove non-content structural tags
        text = re.sub(r'<(head|style|script|meta|link).*?>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 2. Convert Headers
        text = re.sub(r'<h[12].*?>', '\n\n# ', text, flags=re.IGNORECASE)
        text = re.sub(r'<h[34].*?>', '\n\n## ', text, flags=re.IGNORECASE)
        text = re.sub(r'<h[56].*?>', '\n\n### ', text, flags=re.IGNORECASE)

        # 3. Handle structure (dividers, breaks, paragraphs)
        text = re.sub(r'<hr.*?>', '\n\n---\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<(p|div|tr|table).*?>', '\n', text, flags=re.IGNORECASE)
        
        # 4. Lists
        text = re.sub(r'<li>', '\n- ', text, flags=re.IGNORECASE)
        text = re.sub(r'</?(ul|ol).*?>', '\n', text, flags=re.IGNORECASE)

        # 5. Bold and Italic
        text = re.sub(r'<(strong|b).*?>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'</(strong|b)>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'<(em|i).*?>', '*', text, flags=re.IGNORECASE)
        text = re.sub(r'</(em|i)>', '*', text, flags=re.IGNORECASE)

        # 6. Blockquotes
        text = re.sub(r'<blockquote.*?>', '\n> ', text, flags=re.IGNORECASE)

        # 7. Handle Images
        def convert_img(match):
            alt = re.search(r'alt=["\'](.*?)["\']', match.group(0), re.IGNORECASE)
            src = re.search(r'src=["\'].*?/([^/]+?\.(?:png|jpg|jpeg|gif|svg))["\']', match.group(0), re.IGNORECASE)
            text_val = alt.group(1) if alt and alt.group(1).strip() else (src.group(1) if src else "Image")
            return f" ![{text_val}] "
        text = re.sub(r'<img\s+[^>]*?>', convert_img, text, flags=re.IGNORECASE)

        # 5. Convert links to Markdown [text](url)
        def convert_link(match):
            href_m = re.search(r'href=["\'](https?://[^"\']+)["\']', match.group(0), re.IGNORECASE)
            content = match.group(0)
            # Remove the start and end <a> tags to get just the internal content
            content = re.sub(r'^<a.*?>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'</a>$', '', content, flags=re.IGNORECASE)
            
            # Use the internal content but strip remaining HTML tags for the label
            label = re.sub(r'<[^>]+?>', '', content).strip()
            
            if href_m:
                url = href_m.group(1)
                # If there's no text label (like a social icon), use the captured content's symbols or a placeholder
                if not label:
                    # Look for our image placeholder from step 4
                    img_match = re.search(r'!\[(.*?)\]', content)
                    label = img_match.group(1) if img_match else "Link"
                return f" **[{label}]({url})** "
            return label
        
        text = re.sub(r'<a\s+[^>]*?href=["\']https?://[^"\']+?["\'][^>]*?>.*?</a>', convert_link, text, flags=re.DOTALL | re.IGNORECASE)

        # 6. Final Tag Strip
        text = re.sub(r'<[^>]+?>', '', text)
        
        # 7. Cleanup spacing and entities
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&copy;', '©')
        return text.strip()

    return all_plain if all_plain else "(No readable content found)"
