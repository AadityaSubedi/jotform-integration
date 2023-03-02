from typing import Literal, Optional

from pydantic import BaseModel

question_field_type = Literal["text", "phoneNumber", "email"]

form_provider_type = Literal["jotform", "typeform", "googleform"]


class Signin(BaseModel):
    email: str


class Authorize(Signin):
    api_key: str


class Form(BaseModel):
    form_id: str
    provider: form_provider_type = "jotform"
    # data_owner_field: Optional[list[data_owner_field_type]] = None

    # str is the question id
    data_owner_field: Optional[list[str]] = None
    
    

