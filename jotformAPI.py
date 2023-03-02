import socket
import urllib

from fastapi import HTTPException, status
from jotform import JotformAPIClient


class JotFormClient:
    def __init__(self, api_key):
        self.jotformAPIClient = JotformAPIClient(api_key)

    @classmethod
    def safe_request(cls, function, *args, **kwargs):
        # Counter for retries
        retries = 0
        # Maximum number of retries
        max_retries = 3
        response = None

        while retries < max_retries:
            try:
                # make request to get token
                response = function(*args, **kwargs)
                print(response)

                # If the request was successful, break out of the while loop
                break

            except urllib.error.HTTPError:
                raise HTTPException(
                    detail="Internal Server Error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # URLError is thrown when there is a connection error
            except (urllib.error.URLError, socket.timeout):
                retries += 1
                if retries == max_retries:
                    # Raise an exception if the maximum number of retries is reached
                    raise HTTPException(
                        detail="Connection/Timeout error",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
        return response

    def delete_response(self, response_id):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.delete_submission, response_id
        )
        return response

    def get_response(self, response_id):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.get_submission, response_id
        )
        return response

    def get_responses(self, form_id):
        responses = JotFormClient.safe_request(
            self.jotformAPIClient.get_form_submissions, form_id
        )

        return responses

    def delete_form(self, form_id):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.delete_form, form_id
        )
        return response

    def create_form_questions(self, form_id: str, questions_data: str):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.create_form_questions, form_id, questions_data
        )

        return response

    def set_multiple_form_properties(self, form_id: str, properties_data: str):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.set_multiple_form_properties, form_id, properties_data
        )
        return response

    def create_form(self, request_body):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.create_form, request_body
        )
        return response

    def get_form_questions(self, form_id: str) -> dict:
        response = JotFormClient.safe_request(
            self.jotformAPIClient.get_form_questions, form_id
        )

        return response

    def get_form(self, form_id):
        response = JotFormClient.safe_request(self.jotformAPIClient.get_form, form_id)

        return response

    def get_forms(self):
        response = JotFormClient.safe_request(self.jotformAPIClient.get_forms)

        return response

    def get_form_properties(self, form_id):
        response = JotFormClient.safe_request(
            self.jotformAPIClient.get_form_properties, form_id
        )

        return response
