import httpx
import json
from typing import Optional, Annotated, List, Dict, Any
from pydantic.json_schema import SkipJsonSchema
from uuid import UUID

from langchain_core.tools import tool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.integrations.google import validate_google_capability, DRIVE_PROVIDER

DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"

# SCHEMAS
from pydantic import BaseModel, Field

class ListDriveFilesSchema(BaseModel):
    page_size: int = Field(default=10, description="Number of files to return")
    query: Optional[str] = Field(default=None, description="Drive search query (e.g. 'name contains \"report\"', 'mimeType = \"application/pdf\"')")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class ReadDriveFileSchema(BaseModel):
    file_id: str = Field(description="The Google Drive file ID to read")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class CreateDriveFileSchema(BaseModel):
    name: str = Field(description="Name of the file to create")
    content: str = Field(description="String content of the file")
    mime_type: str = Field(default="text/plain", description="MIME type of the file")
    folder_id: Optional[str] = Field(default=None, description="Optional ID of the parent folder")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

# TOOLS

@tool(args_schema=ListDriveFilesSchema)
async def list_drive_files(
    session: AsyncSession,
    user_id: UUID,
    page_size: int = 10,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    List or search for files in the user's Google Drive.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="drive.readonly",
        provider=DRIVE_PROVIDER
    )

    if not auth["authorized"]:
        # Fallback to drive.file if readonly is not granted (user might have only granted .file)
        auth = await validate_google_capability(
            session=session,
            user_id=user_id,
            required_scope_substring="drive.file",
            provider=DRIVE_PROVIDER
        )
        if not auth["authorized"]:
            return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]
    
    params = {
        "pageSize": page_size,
        "fields": "files(id, name, mimeType, modifiedTime, size)",
    }
    if query:
        params["q"] = query

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{DRIVE_API_BASE}/files",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Drive API Error: {resp.text}"}

    data = resp.json()
    return {
        "status": "success",
        "files": data.get("files", [])
    }

@tool(args_schema=ReadDriveFileSchema)
async def read_drive_file_content(
    session: AsyncSession,
    user_id: UUID,
    file_id: str
) -> Dict[str, Any]:
    """
    Read the content of a text-based file from Google Drive (e.g., .txt, .csv, Google Docs).
    Note: For Google Docs, it exports them as plain text.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="drive.readonly",
        provider=DRIVE_PROVIDER
    )

    if not auth["authorized"]:
        auth = await validate_google_capability(
            session=session,
            user_id=user_id,
            required_scope_substring="drive.file",
            provider=DRIVE_PROVIDER
        )
        if not auth["authorized"]:
            return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        # First get metadata to check mimeType
        meta_resp = await client.get(
            f"{DRIVE_API_BASE}/files/{file_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"fields": "name, mimeType"}
        )
        
        if meta_resp.status_code >= 400:
            return {"status": "error", "message": "Could not find file."}
        
        meta = meta_resp.json()
        mime_type = meta.get("mimeType", "")
        
        # If it's a Google Doc, we need to export it
        if mime_type == "application/vnd.google-apps.document":
            resp = await client.get(
                f"{DRIVE_API_BASE}/files/{file_id}/export",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"mimeType": "text/plain"}
            )
        else:
            # Download regular file
            resp = await client.get(
                f"{DRIVE_API_BASE}/files/{file_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"alt": "media"}
            )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Failed to read file content: {resp.text}"}

    return {
        "status": "success",
        "name": meta.get("name"),
        "content": resp.text
    }

@tool(args_schema=CreateDriveFileSchema)
async def create_drive_file(
    session: AsyncSession,
    user_id: UUID,
    name: str,
    content: str,
    mime_type: str = "text/plain",
    folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new file in Google Drive.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="drive.file",
        provider=DRIVE_PROVIDER
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    metadata = {"name": name, "mimeType": mime_type}
    if folder_id:
        metadata["parents"] = [folder_id]

    async with httpx.AsyncClient(timeout=20) as client:
        # Multipart upload for metadata + content
        files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (name, content, mime_type)
        }
        
        resp = await client.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers={"Authorization": f"Bearer {access_token}"},
            files=files
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Drive API Error: {resp.text}"}

    return {
        "status": "success",
        "file": resp.json()
    }
