"""
This module is the main module for the FastAPI app.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

from app.utils.exceptions import UnauthorizedPageException
from app.routers import api, login, reminders, root

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException


# --------------------------------------------------------------------------------
# App Creation
# --------------------------------------------------------------------------------

app = FastAPI()
app.include_router(root.router)
app.include_router(api.router)
app.include_router(login.router)
app.include_router(reminders.router)

import hmac
import hashlib
import subprocess
from fastapi import Header

GITHUB_SECRET = "твой_секрет_из_webhook"

def verify_signature(request_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    sha_name, signature = signature_header.split('=')
    mac = hmac.new(GITHUB_SECRET.encode(), msg=request_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str | None = Header(default=None), x_github_event: str | None = Header(default=None)):
    body = await request.body()

    if not verify_signature(body, x_hub_signature_256):
        return {"status": "invalid signature"}

    if x_github_event == "push":
        # запускаем скрипт деплоя
        subprocess.Popen(["/home/ulyana/devops/deploy.sh"])
        return {"status": "deploy started"}

    return {"status": "ignored event"}

# --------------------------------------------------------------------------------
# Static Files
# --------------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


# --------------------------------------------------------------------------------
# Exception Handlers
# --------------------------------------------------------------------------------

@app.exception_handler(UnauthorizedPageException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedPageException):
  return RedirectResponse('/login?unauthorized=True', status_code=302)


@app.exception_handler(404)
async def page_not_found_exception_handler(request: Request, exc: HTTPException):
  if request.url.path.startswith('/api/'):
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
  else:
    return RedirectResponse('/not-found')


# --------------------------------------------------------------------------------
# OpenAPI Customization
# --------------------------------------------------------------------------------

def custom_openapi():
  if app.openapi_schema:
    return app.openapi_schema
  
  description = \
    """Catty is a web app for tracking reminders.
    It is a full-stack Python app built using FastAPI and HTMX.
    It is meant to be an "example" or "demo" app used for instructional purposes.
    """

  openapi_schema = get_openapi(
    title="Catty: The Reminders App",
    version="1.0.0",
    description=description,
    routes=app.routes,
    tags=[
      {
        "name": "API",
        "description": "Backend API routes for managing reminder lists and items.",
      },
      {
        "name": "Pages",
        "description": "The main Catty web pages.",
      },
      {
        "name": "Authentication",
        "description": "Routes for logging into and out of the app.",
      },
      {
        "name": "HTMX Partials",
        "description": "Routes that serve partial web page contents for HTMX-based requests.",
      },
    ]
  )

  openapi_schema["info"]["x-logo"] = {
    "url": "static/img/logos/catty-500px.png"
  }

  app.openapi_schema = openapi_schema
  return app.openapi_schema


app.openapi = custom_openapi
