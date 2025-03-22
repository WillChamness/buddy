import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, types as pydantic_types
from sqlmodel import Session, create_engine, select
from buddy.src import db
from buddy.src import dependencies
from buddy.src.models import User, UserRoles, RefreshToken, convert_expiry_to_utc
from buddy.src.routers import auth, users


logging.getLogger("passlib").setLevel(logging.ERROR)

app = FastAPI()

_allow_origins: str|None = os.getenv("ALLOW_ORIGINS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in _allow_origins.split(";")] if _allow_origins is not None else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    inline_docs_script_hash = "sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY=" # for the inline script at /docs
    default_src = "default-src 'self';"
    script_src = f"script-src 'self' https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js '{inline_docs_script_hash}';"
    style_src= "style-src 'self' https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css;"
    img_src = "img-src 'self' https://fastapi.tiangolo.com/img/favicon.png;"

    response = await call_next(request)
    response.headers["Content-Security-Policy"] = f"{default_src}{script_src}{style_src}{img_src}"
    return response

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def index() -> str:
    return "Buddy is running"

@app.get("/protected", status_code=200)
def access_protected_route(user: User=Depends(dependencies.get_user_or_admin)) -> str:
    return f"Successfully accessed user resource. User ID: {user.id}"

@app.get("/adminonly", status_code=200)
def access_admin_only_route(admin: User=Depends(dependencies.get_admin)) -> str:
    return f"Successfully accessed admin resource. User ID: {admin.id}"







