from typing import List, Dict, Any

from app.agent.tools.basic_tools import summarize_text, current_user_id
from app.agent.tools.gmail_tools import send_gmail, fetch_recent_gmail, read_gmail_message, verify_delivery
from app.agent.tools.drive_tools import list_drive_files, read_drive_file_content, create_drive_file
from app.agent.tools.sheets_tools import read_spreadsheet_values, update_spreadsheet_values, append_spreadsheet_values, create_spreadsheet
from app.agent.tools.github_tools import list_github_repositories, list_github_issues, create_github_issue, read_github_file_content

# 1. THE COMPLETE TOOLS LIST
# This is the list that will be bound to the LLM
ALL_TOOLS = [
    summarize_text,
    current_user_id,
    send_gmail,
    fetch_recent_gmail,
    read_gmail_message,
    verify_delivery,
    list_drive_files,
    read_drive_file_content,
    create_drive_file,
    read_spreadsheet_values,
    update_spreadsheet_values,
    append_spreadsheet_values,
    create_spreadsheet,
    list_github_repositories,
    list_github_issues,
    create_github_issue,
    read_github_file_content,
]

# 2. HITL REGISTRY
# Names of tools that MUST go through the approval workflow
TOOLS_REQUIRING_APPROVAL = [
    "send_gmail",
    "create_drive_file",
    "update_spreadsheet_values",
    "append_spreadsheet_values",
    "create_spreadsheet",
    "create_github_issue",
]

# 3. HELPER MAPS
# Allows quick lookup of tool objects by their names
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

def get_tool_by_name(name: str):
    return TOOL_MAP.get(name)

def is_approval_required(tool_name: str) -> bool:
    return tool_name in TOOLS_REQUIRING_APPROVAL
