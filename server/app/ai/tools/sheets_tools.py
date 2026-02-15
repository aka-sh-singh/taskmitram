import httpx
import json
from typing import Optional, Annotated, List, Dict, Any
from pydantic.json_schema import SkipJsonSchema
from uuid import UUID

from langchain_core.tools import tool
from sqlmodel.ext.asyncio.session import AsyncSession

from app.integrations.google import validate_google_capability, SHEETS_PROVIDER

SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets"

# SCHEMAS
from pydantic import BaseModel, Field

class ReadSheetSchema(BaseModel):
    spreadsheet_id: str = Field(description="The ID of the spreadsheet to read")
    range_name: str = Field(description="The A1 notation of the range to read (e.g. 'Sheet1!A1:E10')")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class UpdateSheetSchema(BaseModel):
    spreadsheet_id: str = Field(description="The ID of the spreadsheet to update")
    range_name: str = Field(description="The A1 notation of the range to update")
    values: List[List[Any]] = Field(description="The data to write (list of rows)")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

class CreateSheetSchema(BaseModel):
    title: str = Field(description="Title of the new spreadsheet")
    session: Annotated[Optional[Any], SkipJsonSchema()] = None
    user_id: Annotated[Optional[Any], SkipJsonSchema()] = None

# TOOLS

@tool(args_schema=ReadSheetSchema)
async def read_spreadsheet_values(
    session: AsyncSession,
    user_id: UUID,
    spreadsheet_id: str,
    range_name: str
) -> Dict[str, Any]:
    """
    Read values from a specific range in a Google Spreadsheet.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="spreadsheets.readonly",
        provider=SHEETS_PROVIDER
    )

    if not auth["authorized"]:
        auth = await validate_google_capability(
            session=session,
            user_id=user_id,
            required_scope_substring="spreadsheets",
            provider=SHEETS_PROVIDER
        )
        if not auth["authorized"]:
            return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{range_name}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Sheets API Error: {resp.text}"}

    data = resp.json()
    return {
        "status": "success",
        "values": data.get("values", [])
    }

@tool(args_schema=UpdateSheetSchema)
async def update_spreadsheet_values(
    session: AsyncSession,
    user_id: UUID,
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """
    Update values in a specific range of a Google Spreadsheet.
    Overwrite existing data in that range.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="spreadsheets",
        provider=SHEETS_PROVIDER
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.put(
            f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{range_name}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"valueInputOption": "RAW"},
            json={
                "values": values
            }
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Sheets API Error: {resp.text}"}

    return {
        "status": "success",
        "updated_cells": resp.json().get("updatedCells")
    }

@tool(args_schema=UpdateSheetSchema)
async def append_spreadsheet_values(
    session: AsyncSession,
    user_id: UUID,
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]]
) -> Dict[str, Any]:
    """
    Append values to a table in a Google Spreadsheet. 
    Finds the first empty row after the range and adds data there.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="spreadsheets",
        provider=SHEETS_PROVIDER
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{range_name}:append",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
            json={
                "values": values
            }
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Sheets API Error: {resp.text}"}

    return {
        "status": "success",
        "updates": resp.json().get("updates")
    }

@tool(args_schema=CreateSheetSchema)
async def create_spreadsheet(
    session: AsyncSession,
    user_id: UUID,
    title: str
) -> Dict[str, Any]:
    """
    Create a new empty Google Spreadsheet.
    """
    auth = await validate_google_capability(
        session=session,
        user_id=user_id,
        required_scope_substring="spreadsheets",
        provider=SHEETS_PROVIDER
    )

    if not auth["authorized"]:
        return {"status": "error", "message": auth["error"]}

    access_token = auth["access_token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{SHEETS_API_BASE}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "properties": {"title": title}
            }
        )

    if resp.status_code >= 400:
        return {"status": "error", "message": f"Sheets API Error: {resp.text}"}

    data = resp.json()
    return {
        "status": "success",
        "spreadsheet_id": data.get("spreadsheetId"),
        "spreadsheet_url": data.get("spreadsheetUrl")
    }
