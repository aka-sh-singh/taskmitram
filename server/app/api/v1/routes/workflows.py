from fastapi import APIRouter

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Get workflow details by ID.
    Placeholder endpoint for future implementation.
    """
    return {
        "id": workflow_id,
        "status": "draft",
        "message": "Workflow endpoint placeholder"
    }
