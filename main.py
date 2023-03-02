"""
main.py
"""
from typing import Any, Dict

# import ujson
# from bson.json_util import dumps
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import routers
from common.base.plugin import register_plugin_class
from components import UserInfo
from models import Signin

router = APIRouter(
    prefix="/api",
    tags=["jot",],
)

app = FastAPI()


db: Dict[str, Any] = {"api_key": ""}  # store the tokens


origins = ["http://localhost:3000", "http://localhost:8000", "http://localhost"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/signin")
async def signin(request: Request, data: Signin):
    # data = await request.json()
    # store in database
    email = data.email
    _ = UserInfo(email=email).save()
    return JSONResponse(
        content={"message": "sign in succesfully"}, status_code=status.HTTP_201_CREATED
    )


# include the router


register_plugin_class(router=routers.router, route=routers.JotformRoutes(), tags=["jotform"])
app.include_router(routers.router)
app.include_router(router)
