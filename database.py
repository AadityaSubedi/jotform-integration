import os
from typing import Any, Iterable, List, Mapping, Optional, Union

import pymongo
from pymongo.results import InsertManyResult, InsertOneResult


class DB:
    # Private variables (DONOT access outside the class)
    _build = os.environ.get("BUILD", "dev")
    _client = pymongo.MongoClient()

    if _build == "dev":
        database = _client.jotform_dev
    elif _build == "staging":
        database = _client.jotform_staging
    elif _build == "prod":
        database = _client.jotform

    # The following methods are used when we expect to work with
    # only one document of a collection.
    # These operate on the first document that matches in the collection.
    # Usually, these methods are recommended to use.
    @staticmethod
    def insert_one(collection: str, data: dict) -> InsertOneResult:
        """
        Insert one document to a collection.
        Args:
            collection (str): The collection to insert to
            data (dict): The data to insert
        Returns:
            InsertOneResult: Returns if succesfull else prints error
        """
        try:
            return DB.database[collection].insert_one(data)
        except pymongo.errors.DuplicateKeyError as dupErr:
            raise Exception(
                f"Duplicated data entry for the {collection} collection "
                f"for {dupErr.details['keyValue']}"
            )

    @staticmethod
    def find_one_and_update(
        collection: str,
        query: Mapping[str, Any],
        data: dict,
        action: str = "$set",
        return_values: Union[Mapping[str, bool], List[str]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Find a document which matches the query in the collection and update it.
        Args:
            collection (str): Collection Name
            query (Mapping[str, Any], optional): filter query. Defaults to None.
            return_values (Union[Mapping[str, bool], List[str]], optional):
                The keys to return. Defaults to None.
        Returns:
            Optional[Mapping[str, Any]]: Returns the document if found else None
        """
        return DB.database[collection].find_one_and_update(
            query, {action: data}, return_values
        )

    @staticmethod
    def find_one(
        collection: str,
        query: Mapping[str, Any] = None,
        return_values: Union[Mapping[str, bool], List[str]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Find a document which matches the query in the collection.
        Args:
            collection (str): Collection Name
            query (Mapping[str, Any], optional): filter query. Defaults to None.
            return_values (Union[Mapping[str, bool], List[str]], optional):
                The keys to return. Defaults to None.
        Returns:
            Optional[Mapping[str, Any]]: Returns the document if found else None
        """
        return DB.database[collection].find_one(query, return_values)

    @staticmethod
    def insert_many(collection: str, data: Iterable[dict]) -> InsertManyResult:
        """
        Inserts more than one document in a collection.
        Args:
            collection (str): Collection to insert to
            data (dict): The data to insert
        Returns:
            InsertManyResult: Information about Insertion
        """
        return DB.database[collection].insert_many(data)
