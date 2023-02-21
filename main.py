"""
main.py
"""
from typing import Any, Dict

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jotform import JotformAPIClient

from components import JotForm, UserInfo
from database import DB

router = APIRouter(
    prefix="/jot/auth",
    tags=["jot", "auth"],
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
async def signin(request: Request):
    data = await request.json()
    # store in database
    username = data["username"]
    _ = UserInfo(username=username).save()
    return JSONResponse(
        content={"message": "sign in succesfully"}, status_code=status.HTTP_200_OK
    )


@router.post("/oauth2callback")
async def callback(request: Request):
    try:
        print("here1")
        data = await request.json()
        # store in database
        api_key = data["api_key"]
        username = data["username"]
        print("here")
        _ = UserInfo.update(username=username, data={"jot_api": api_key})

        return JSONResponse(
            content={"message": "jot api updated succesfully"},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/forms")
async def get_all_forms(username: str):
    api_key = DB.find_one("UserDocument", {"username": username})["jot_api"]

    jotformAPIClient = JotformAPIClient(api_key)
    forms = jotformAPIClient.get_forms()
    forms = jsonable_encoder(forms)
    return JSONResponse(content=forms, status_code=status.HTTP_200_OK)


@router.get("/import/form/{form_id}")
async def get_form(form_id: str, username: str):
    try:
        api_key = DB.find_one("UserDocument", {"username": username})["jot_api"]

        jotform = JotForm(form_id, api_key)
        jotform.save()
        form = jotform.json()
        form = jsonable_encoder(form)

        return JSONResponse(content=form, status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/form/{form_id}/submissions")
async def get_all_form_submission(form_id: str):
    jotformAPIClient = JotformAPIClient(db["api_key"])
    submissions = jotformAPIClient.get_form_submissions(form_id)
    submissions = jsonable_encoder(submissions)
    return JSONResponse(content=submissions, status_code=status.HTTP_200_OK)


@router.get("/submission/{submission_id}")
async def get_form_submission(submission_id: str):
    jotformAPIClient = JotformAPIClient(db["api_key"])
    submission = jotformAPIClient.get_submission(submission_id)
    submission = jsonable_encoder(submission)
    return JSONResponse(content=submission, status_code=status.HTTP_200_OK)


# include the router
app.include_router(router)
