import json
from typing import Any, Dict, Optional

from fastapi import Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from common.base.plugin import BasePluginRoute, FormProvider
from common.utils.router import CustomAPIRouter
from components import JotForm, JotFormClient, UserInfo
from database import DB
from models import Authorize

router = CustomAPIRouter(
    prefix="/api",
    tags=["jotform"],
)


class JotformRoutes(BasePluginRoute):
    async def authorize(
        self,
        request: Request,
        email: str,
        provider: str | FormProvider,
        data: Authorize,
    ):
        api_key = data.api_key
        email = data.email

        _ = UserInfo.update(email=email, data={"credentials.api_key": api_key})

        return JSONResponse(
            content={"message": "jot api updated succesfully"},
            status_code=status.HTTP_202_ACCEPTED,
        )

    async def callback(self, request: Request, provider: str | FormProvider):
        raise NotImplementedError

    async def revoke(self, email: str, provider: str | FormProvider):
        _ = UserInfo.update(email=email, data={"credentials.api_key": None})
        return JSONResponse(
            content={"message": "jot api revoked succesfully"},
            status_code=status.HTTP_200_OK,
        )

    async def list_forms(self, email: str, provider: str | FormProvider):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        forms = jotFormClient.get_forms()
        forms = jsonable_encoder(forms)
        return JSONResponse(content=forms, status_code=status.HTTP_200_OK)

    async def get_form(self, form_id: str, email: str, provider: str | FormProvider):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotform = JotForm(form_id, api_key)
        form = jotform.get_form()
        form = jsonable_encoder(form)

        return JSONResponse(content=form, status_code=status.HTTP_200_OK)

    async def import_form(
        self,
        form_id: str,
        email: str,
        provider: str | FormProvider,
        data_owner_field: Optional[str] = None,
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]

        jotform = JotForm(form_id, api_key, provider, data_owner_field)
        jotform.save()

        return JSONResponse(
            content={"message": "form succesfully imported"},
            status_code=status.HTTP_200_OK,
        )

    async def create_form(
        self,
        email: str,
        provider: str | FormProvider,
        request_body: Dict[str, Any] = Body(...),
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        response = jotFormClient.create_form(request_body)
        response = jsonable_encoder(response)

        return JSONResponse(content=response, status_code=status.HTTP_201_CREATED)

    async def update_form(
        self,
        form_id: str,
        email: str,
        provider: str | FormProvider,
        request_body: Dict[str, Any] = Body(...),
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)

        # jotform doesnt provide any PUT method endpoint for updating form at once,
        # so we have to update the form questions and properties separately

        # TODO: Make update operation atomic -> revert the questions update if the properties update fails
        
        # update the questions
        questions = {"questions": request_body["questions"]}
        questions_data = json.dumps(questions)
        _ = jotFormClient.create_form_questions(form_id, questions_data)

        # update the properties
        properties = {"properties": request_body["questions"]}
        properties_data = json.dumps(properties)
        _ = jotFormClient.set_multiple_form_properties(form_id, properties_data)

        return JSONResponse(
            content="form updated succesfully", status_code=status.HTTP_200_OK
        )

    async def delete_form(self, form_id: str, email: str, provider: str | FormProvider):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        _ = jotFormClient.delete_form(form_id)
        return JSONResponse(
            content="form deleted succesfully", status_code=status.HTTP_200_OK
        )

    async def list_form_responses(
        self, form_id: str, email: str, provider: str | FormProvider
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        responses = jotFormClient.get_responses(form_id)
        responses = jsonable_encoder(responses)

        return JSONResponse(content=responses, status_code=status.HTTP_200_OK)

    async def get_form_response(
        self, form_id: str, email: str, response_id: str, provider: str | FormProvider
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        response = jotFormClient.get_response(response_id)
        response = jsonable_encoder(response)

        return JSONResponse(content=response, status_code=status.HTTP_200_OK)

    async def delete_form_response(
        self, form_id: str, email: str, response_id: str, provider: str | FormProvider
    ):
        api_key = DB.find_one(UserInfo.collection, {"email": email})["credentials"][
            "api_key"
        ]
        jotFormClient = JotFormClient(api_key)
        _ = jotFormClient.delete_response(response_id)
        return JSONResponse(
            content="response deleted succesfully", status_code=status.HTTP_200_OK
        )
