from fastapi import HTTPException, status

from database import DB
from jotformAPI import JotFormClient


class UserInfo:
    collection = "UserDocument"

    def __init__(self, email: str, api_key=None, provider: str = "jotform"):
        self.email = email
        self.api_key = api_key
        self.provider = provider

    def save(self):
        return DB.insert_one(self.collection, data=self.json())

    @staticmethod
    def update(email: str, data: dict):
        # find the user
        _ = DB.find_one_and_update(UserInfo.collection, {"email": email}, data)

    def json(self):
        return {
            "email": self.email,
            "provider": self.provider,
            "credentials": {
                "api_key": self.api_key,
            },
        }


class JotForm:
    collection = "JotForm"

    class Submissions:
        collection = "Submissions"

        def __init__(
            self,
            form_id: str,
            jotFormClient: JotFormClient,
        ):
            self.form_id = form_id
            self.jotFormClient = jotFormClient

        def save(self):
            return DB.insert_many(self.collection, data=self.json())

        def json(self):
            submissions = self.get_submissions()

            def adjust_id_to_response_id(submission):
                # change the id of submission to response_id
                submission["response_id"] = submission["id"]
                del submission["id"]
                return submission

            submissions = map(adjust_id_to_response_id, submissions)

            return [
                {
                    **submission,
                    "provider": "jotform",
                }
                for submission in submissions
            ]

        def get_submissions(self):
            submissions = self.jotFormClient.get_responses(self.form_id)
            return submissions

    def __init__(
        self,
        form_id: str,
        api_key: str,
        provider: str = "jotform",
        data_owner_fields: list = [],
    ):
        self.form_id = form_id
        self.api_key = api_key
        self.jotFormClient = JotFormClient(api_key)
        self.provider = provider
        # validate data owner field names
        self.data_owner_fields = self.validate_data_owner_fields(data_owner_fields)

    def save(self):
        _ = JotForm.Submissions(self.form_id, self.jotFormClient).save()
        # print(_.inserted_ids)

        return DB.insert_one(self.collection, data=self.json())

    def validate_data_owner_fields(self, data_owner_fields: list):
        valid_data_owner_fields = ["text", "phoneNumber", "email"]

        questions: dict = self.jotFormClient.get_form_questions(self.form_id)

        for field in data_owner_fields:
            if questions[field]["name"] not in valid_data_owner_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid data owner field",
                )

        return data_owner_fields

    def json(self):
        self.form = self.get_form()
        return {
            "api_key": self.api_key,
            "form_id": self.form_id,
            "provider": self.provider,
            "data_owner_fields": self.data_owner_fields,
            "form": self.form,
        }

    def get_form(self):
        form = self.jotFormClient.get_form(self.form_id)

        # get the properties of the form and add them
        properties = self.jotFormClient.get_form_properties(self.form_id)

        # add the details like questions;
        questions = self.jotFormClient.get_form_questions(self.form_id)

        # merge them into form
        form["properties"] = properties
        form["questions"] = questions

        return form

    @staticmethod
    def find_one(form_id: str):
        return DB.find_one(JotForm.collection, {"form_id": form_id})


# TODO: add the pydantic model for the JotForm : exploring beanie
