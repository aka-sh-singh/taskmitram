from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from scalar_fastapi import get_scalar_api_reference

from app.db.session import init_db
from app.api.v1.router import router as v1_router


# LIFESPAN (startup & shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startupt
    await init_db()
    print(" Server started. Database initialized.")
    
    yield
    
    # shutdwn
    print(" Server shutting down.")



# FASTAPI APP SETUP
app = FastAPI(
    title="Taskmitra",
    version="1.0.0",
    docs_url=None,        
    redoc_url=None,      
    lifespan=lifespan,
)



# CORS SETTINGS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Chat-Id"],
    max_age=600,
)



# REGISTER API ROUTES
app.include_router(v1_router, prefix="/api")



# CUSTOM DOCS ROUTE USING SCALAR
@app.get("/docs", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Taskmitra"
    )
