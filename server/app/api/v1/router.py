from fastapi import APIRouter

# Import route modules
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.chats import router as chats_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.integrations_google import router as google_router
from app.api.v1.routes.integrations_drive import router as drive_router
from app.api.v1.routes.integrations_sheets import router as sheets_router
from app.api.v1.routes.integrations_github import router as github_router
from app.api.v1.routes.integrations_status import router as status_router
from app.api.v1.routes.approvals import router as approvals_router
from app.api.v1.routes.workflows import router as workflows_router

# Create main v1 router
router = APIRouter(prefix="/v1")

# Attach each route group
router.include_router(auth_router)
router.include_router(chats_router)
router.include_router(users_router)
router.include_router(google_router)
router.include_router(drive_router)
router.include_router(sheets_router)
router.include_router(github_router)
router.include_router(status_router)
router.include_router(approvals_router, prefix="/approvals", tags=["Approvals"])
router.include_router(workflows_router)
