""" Holds the WikibaseSession class and other functionality related to network accesses. """

import configparser
import json
import logging
import os
import time
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

import tfsl.interfaces as I

maxlag: int = 5

token_request_params = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json",
}

csrf_token_params = {
    "action": "query",
    "meta": "tokens",
    "format": "json"
}

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
DEFAULT_USER_AGENT = 'tfsl 0.0.1'

class WikibaseSession:
    """ Auth library for Wikibases. """
    def __init__(self,
                 username: str,
                 password: Optional[str] = None,
                 token: Optional[str] = None,
                 user_agent: str = DEFAULT_USER_AGENT,
                 url: str = WIKIDATA_API_URL
                 ):
        self.url = url
        self.user_agent = user_agent
        self.headers = {"User-Agent": user_agent}
        self.session = requests.Session()

        self.username = username
        self.assert_user = None
        if password is not None:
            self._password = password
        else:
            self._password = getpass(f"Enter password for {self.username}: ")

        token_response = self.get(token_request_params)
        login_token = token_response["query"]["tokens"]["logintoken"]

        connection_request_params = {
            "action": "login",
            "format": "json",
            "lgname": self.username,
            "lgpassword": self._password,
            "lgtoken": login_token,
        }
        connection_response = self.post(connection_request_params, 30)
        if connection_response.get("login", []).get("result") != "Success":
            raise PermissionError("Login failed", connection_response["login"]["reason"])
        logging.info("Log in succeeded")

        if token is not None:
            self.csrf_token = token
            logging.info("Using CSRF token: %s", self.csrf_token)
        else:
            csrf_response = self.get(csrf_token_params)
            self.csrf_token = csrf_response["query"]["tokens"]["csrftoken"]
            logging.info("Got CSRF token: %s", self.csrf_token)

        if username is not None:
            # truncate bot name if a "bot password" is used
            self.assert_user = username.split("@")[0]

    def push(self, obj_in: I.Entity, summary: Optional[str]=None, maxlag_in: int=maxlag, bot: bool=False) -> Any:
        """ Post data to Wikibase. """
        data = obj_in.__jsonout__()
        requestjson = {"action": "wbeditentity", "format": "json"}
        if bot:
            requestjson["bot"] = ""

        if not data.get("id", False):
            if data.get("lexicalCategory", False):
                requestjson["new"] = "lexeme"
            elif data.get("glosses", False):
                requestjson["new"] = "sense"
            elif data.get("representations", False):
                requestjson["new"] = "form"
            elif data.get("labels", False) and data.get("sitelinks", False):
                requestjson["new"] = "item"
            else:
                requestjson["new"] = "property"
        else:
            requestjson["id"] = data["id"]

        if summary is not None:
            requestjson["summary"] = summary
        if self.assert_user is not None:
            requestjson["assertuser"] = self.assert_user

        requestjson["token"] = self.csrf_token
        requestjson["data"] = json.dumps(data)
        requestjson["maxlag"] = str(maxlag_in)

        push_response = self.session.post(self.url,
            data=requestjson, headers=self.headers, auth=None)
        if push_response.status_code != 200:
            error_msg = f"POST unsuccessful ({push_response.status_code}): {push_response.text}"
            raise Exception(error_msg)

        push_response_data = push_response.json()
        if "error" in push_response_data:
            if push_response_data["error"]["code"] == "maxlag":
                sleepfor = float(push_response.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.push(obj_in)
            else:
                raise PermissionError("API returned error: " + str(push_response_data["error"]))

        logging.debug("Post request succeed")
        return push_response_data

    def post(self, data: Dict[str, str], maxlag_in: int=maxlag) -> Any:
        """ Post data to Wikibase. The CSRF token is automatically
            filled in if __AUTO__ is given instead.

            :param data: Parameters to send via POST
            :return: Answer from the server
        """
        if data.get("token") == "__AUTO__":
            data["token"] = self.csrf_token
        if "assertuser" not in data and self.assert_user is not None:
            data["assertuser"] = self.assert_user
        data["maxlag"] = str(maxlag_in)

        post_response = self.session.post(self.url, data=data, headers=self.headers, auth=None)
        if post_response.status_code != 200:
            error_msg = f"POST unsuccessful ({post_response.status_code}): {post_response.text}"
            raise Exception(error_msg)

        post_response_data = post_response.json()
        if "error" in post_response_data:
            if post_response_data["error"]["code"] == "maxlag":
                sleepfor = float(post_response.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.post(data)
            else:
                raise PermissionError("API returned error: " + str(post_response_data["error"]))

        logging.debug("Post request succeed")
        return post_response_data

    def get(self, data: Dict[str, str]) -> Any:
        """ Send a GET request to Wikibase.

            :param data: Parameters to send via GET
            :return: Answer from the server
        """
        get_response = self.session.get(self.url, params=data, headers=self.headers)
        get_response_data = get_response.json()
        if get_response.status_code != 200 or "error" in get_response_data:
            # We do not set maxlag for GET requests – so this error can only
            # occur if the users sets maxlag in the request data object
            if get_response_data["error"]["code"] == "maxlag":
                sleepfor = float(get_response.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.get(data)
            else:
                raise Exception(f"GET unsuccessful ({get_response.status_code}): {get_response.text}")
        logging.debug("Get request succeed")
        return get_response_data

def get_wikidata_entities(lids: List[I.EntityId], user_agent: str=DEFAULT_USER_AGENT) -> Dict[I.EntityId, I.EntityPublishedSettings]:
    """ Retrieves a list of entities using the Wikidata API. """
    query_parameters = {
        "action": "wbgetentities",
        "format": "json",
        "ids": "|".join(lids)
    }
    current_headers = {
        "User-Agent": user_agent
    }
    get_response = requests.get(WIKIDATA_API_URL, params=query_parameters, headers=current_headers)
    data_output = get_response.json()
    if get_response.status_code != 200 or "error" in data_output:
        raise PermissionError("API returned error: " + str(data_output["error"]))
    if isinstance(data_output, dict):
        returned_entities: Dict[I.EntityId, I.EntityPublishedSettings] = data_output["entities"]
        return returned_entities
    raise ValueError(f"Response from retrieving {lids} not valid JSON")

def read_config() -> Tuple[str, float]:
    """ Reads the config file residing at /path/to/tfsl/config.ini. """
    config = configparser.ConfigParser()
    current_config_path = (Path(__file__).parent / '../config.ini').resolve()
    config.read(current_config_path)
    cpath = config['Tfsl']['CachePath']
    ttl = float(config['Tfsl']['TimeToLive'])
    return cpath, ttl

cache_path, time_to_live = read_config()
os.makedirs(cache_path,exist_ok=True)

def get_filename(entity_name: str) -> str:
    """ Constructs the name of a text file containing a sense subgraph based on a given property. """
    return os.path.join(cache_path, f"{entity_name}.json")

def retrieve_single_entity(entity: Union[I.Qid, I.Pid, I.Lid]) -> I.EntityPublishedSettings:
    """ Retrieves the JSON for a single Wikibase entity. """
    filename = get_filename(entity)
    try:
        assert time.time() - os.path.getmtime(filename) < time_to_live
        with open(filename, encoding="utf-8") as fileptr:
            current_output = json.load(fileptr)
    except (FileNotFoundError, OSError, AssertionError):
        current_entities = get_wikidata_entities([entity])
        current_output = current_entities[entity]
        with open(filename, "w", encoding="utf-8") as fileptr:
            json.dump(current_output, fileptr)
    if not I.is_EntityPublishedSettings(current_output):
        raise ValueError(f"Retrieved data for {entity} was not an entity")
    return current_output
