from jotform import JotformAPIClient

from database import DB


class UserInfo:
    collection = "UserDocument"

    def __init__(self, username: str, jot_api=None):
        self.username = username
        self.jot_api = jot_api

    def save(self):
        return DB.insert_one(self.collection, data=self.json())

    @staticmethod
    def update(username:str, data:dict):
        # find the user
        _ = DB.find_one_and_update(UserInfo.collection, {"username": username}, data)

    def json(self):
        return {
            "username": self.username,
            "jot_api": self.jot_api,
        }


class JotForm:
    collection = "JotForm"

    def __init__(self, form_id, api_key):
        self.form_id = form_id
        self.api_key = api_key
        self.jotformAPIClient = JotformAPIClient(api_key)

    def save(self):
        return DB.insert_one(self.collection, data=self.json())

    def json(self):
        return {
            "api_key": self.api_key,
            "form": self.get_form(),
        }

    def get_form(self):
        form = self.jotformAPIClient.get_form(self.form_id)

        form = self.associate_submissions(form)

        return form

    def associate_submissions(self, form):
        submissions = self.jotformAPIClient.get_form_submissions(self.form_id)

        form["submissions"] = submissions

        return form
