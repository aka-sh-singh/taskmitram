import httpx
import json
from typing import Optional, Annotated, List, Dict, Any
from pydantic.json_schema import SkipJsonSchema
from uuid import UUID

from langchain_core.tools import tool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.integrations.github import validate_github_capability

GITHUB_API_BASE = "https://api.github.com"

# SCHEMAS
from pydantic import BaseModel, Field

class ListReposSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    limit: int = Field(default=10, description="Number of repositories to return")
    
    # Injected fields
    session: Annotated[Optional[AsyncSession], SkipJsonSchema()] = Field(default=None)
    user_id: Annotated[Optional[UUID], SkipJsonSchema()] = Field(default=None)

class ListIssuesSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    owner: str = Field(description="The GitHub username or organization name")
    repo: str = Field(description="The repository name")
    state: str = Field(default="open", description="Issue state: 'open', 'closed', or 'all'")
    
    # Injected fields
    session: Annotated[Optional[AsyncSession], SkipJsonSchema()] = Field(default=None)
    user_id: Annotated[Optional[UUID], SkipJsonSchema()] = Field(default=None)

class CreateIssueSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    owner: str = Field(description="The GitHub username or organization name")
    repo: str = Field(description="The repository name")
    title: str = Field(description="The title of the issue")
    body: Optional[str] = Field(default=None, description="The body/description of the issue")
    
    # Injected fields
    session: Annotated[Optional[AsyncSession], SkipJsonSchema()] = Field(default=None)
    user_id: Annotated[Optional[UUID], SkipJsonSchema()] = Field(default=None)

class ReadGithubFileSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    path: str = Field(description="Path to the file in the repository")
    branch: str = Field(default="main", description="Branch name")
    
    # Injected fields
    session: Annotated[Optional[AsyncSession], SkipJsonSchema()] = Field(default=None)
    user_id: Annotated[Optional[UUID], SkipJsonSchema()] = Field(default=None)

# TOOLS

@tool(args_schema=ListReposSchema)
async def list_github_repositories(
    session: AsyncSession,
    user_id: UUID,
    limit: int = 10
) -> str:
    """
    List the authenticated user's GitHub repositories.
    """
    auth = await validate_github_capability(session, user_id, "repo")
    if not auth["authorized"]:
        return auth["error"]

    access_token = auth["access_token"]
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GITHUB_API_BASE}/user/repos",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            params={"sort": "updated", "per_page": limit}
        )

    if resp.status_code >= 400:
        return json.dumps({"status": "error", "message": f"GitHub API Error: {resp.text}"})

    repos = resp.json()
    formatted_repos = [
        {"name": r["full_name"], "description": r["description"], "url": r["html_url"], "stars": r["stargazers_count"]}
        for r in repos
    ]
    
    return json.dumps({"status": "success", "repositories": formatted_repos})

@tool(args_schema=ListIssuesSchema)
async def list_github_issues(
    session: AsyncSession,
    user_id: UUID,
    owner: str,
    repo: str,
    state: str = "open"
) -> str:
    """
    List issues for a specific GitHub repository.
    """
    auth = await validate_github_capability(session, user_id, "repo")
    if not auth["authorized"]:
        return auth["error"]

    access_token = auth["access_token"]
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            params={"state": state}
        )

    if resp.status_code >= 400:
        return json.dumps({"status": "error", "message": f"GitHub API Error: {resp.text}"})

    issues = resp.json()
    formatted_issues = [
        {"number": i["number"], "title": i["title"], "user": i["user"]["login"], "state": i["state"], "url": i["html_url"]}
        for i in issues if "pull_request" not in i  # Only real issues, not PRs
    ]
    
    return json.dumps({"status": "success", "issues": formatted_issues})

@tool(args_schema=CreateIssueSchema)
async def create_github_issue(
    session: AsyncSession,
    user_id: UUID,
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None
) -> str:
    """
    Create a new issue in a GitHub repository.
    """
    auth = await validate_github_capability(session, user_id, "repo")
    if not auth["authorized"]:
        return auth["error"]

    access_token = auth["access_token"]
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"title": title, "body": body}
        )

    if resp.status_code >= 400:
        return json.dumps({"status": "error", "message": f"GitHub API Error: {resp.text}"})

    issue = resp.json()
    return json.dumps({
        "status": "success", 
        "message": "Issue created", 
        "url": issue["html_url"],
        "number": issue["number"]
    })

@tool(args_schema=ReadGithubFileSchema)
async def read_github_file_content(
    session: AsyncSession,
    user_id: UUID,
    owner: str,
    repo: str,
    path: str,
    branch: str = "main"
) -> str:
    """
    Read the raw content of a file from a GitHub repository.
    """
    auth = await validate_github_capability(session, user_id, "repo")
    if not auth["authorized"]:
        return auth["error"]

    access_token = auth["access_token"]
    
    async with httpx.AsyncClient(timeout=15) as client:
        # Get raw content from raw.githubusercontent.com or via API
        # Using API content with explicit header for raw data
        resp = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3.raw"
            },
            params={"ref": branch}
        )

    if resp.status_code >= 400:
        return json.dumps({"status": "error", "message": f"GitHub API Error: {resp.text}"})

    return json.dumps({
        "status": "success",
        "path": path,
        "content": resp.text
    })
