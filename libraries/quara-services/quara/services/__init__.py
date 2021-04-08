"""This module provides The Service and ServiceRouter classes as well as useful imports when developing HTTP applications."""
from fastapi import (
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    WebSocket,
    status,
)
from fastapi.encoders import jsonable_encoder

from .routing import ServiceRouter
from .services import Service
