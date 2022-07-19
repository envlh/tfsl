from getpass import getpass
from typing import Any, Dict, List, Optional

import json
import logging
import time
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
                 username,
                 password: Optional[str] = None,
                 token: Optional[str] = None,
                 auth: Optional[str] = None,
                 user_agent: str = DEFAULT_USER_AGENT,
                 URL: str = WIKIDATA_API_URL
                 ):
        self.url = URL
        self.user_agent = user_agent
        self.auth = auth
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

    def push(self, obj_in, summary=None, maxlag_in=maxlag) -> Any:
        """Post data to Wikibase.
        """
        data = obj_in.__jsonout__()
        requestjson = {"action": "wbeditentity", "format": "json"}

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

        requestjson["token"] = self.csrf_token

        data = obj_in.__jsonout__()
        requestjson["data"] = json.dumps(data)

        requestjson["assertuser"] = self.assert_user

        requestjson["maxlag"] = str(maxlag_in)

        push_response = self.session.post(self.url,
            data=requestjson, headers=self.headers, auth=self.auth)
        if push_response.status_code != 200:
            error_msg = f"POST unsuccessful ({push_response.status_code}): {push_response.text}"
            raise Exception(error_msg)

        push_response_data = push_response.json()
        if "error" in push_response_data:
            if push_response_data["error"]["code"] == "maxlag":
                sleepfor = float(push_response.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.push(data)
            else:
                raise PermissionError("API returned error: " + str(push_response_data["error"]))

        logging.debug("Post request succeed")
        return push_response_data

    def post(self, data: Dict[str, str], maxlag_in=maxlag) -> Any:
        """Post data to Wikibase. The CSRF token is automatically
        filled in if __AUTO__ is given instead.

        :param data: Parameters to send via POST
        :type  data: Dict[str, str])
        :returns: Answer form the server as Objekt
        :rtype: Any

        """
        if data.get("token") == "__AUTO__":
            data["token"] = self.csrf_token
        if "assertuser" not in data and self.assert_user is not None:
            data["assertuser"] = self.assert_user
        data["maxlag"] = str(maxlag_in)

        post_response = self.session.post(self.url, data=data, headers=self.headers, auth=self.auth)
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
        """Send a GET request to wikidata

        :param data: Parameters to send via GET
        :type  data: Dict[str, str]
        :returns: Answer form the server as Objekt
        :rtype: Any

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
                raise Exception(
                    "GET unsuccessful ({}): {}".format(get_response.status_code, get_response.text)
                )
        logging.debug("Get request succeed")
        return get_response_data

    def find_lexeme(self, lemma, language, category,
        entity_prefix='http://www.wikidata.org/entity/',
        query_url="https://query.wikidata.org/sparql"):
        # TODO: have a method in lexeme.py that returns each lexeme from the result list?
        # TODO: handle multiple combos of one of these inputs?
        # TODO: make the query customizable?
        query_in = f"""
        SELECT ?i {{
            ?i dct:language wd:{language.item} ;
               wikibase:lemma '{lemma.text}'@{lemma.language.code} ;
               wikibase:lexicalCategory wd:{category}
        }}
        """
        query_parameters = {
            "query": query_in
        }
        query_headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": self.user_agent
        }
        find_response = requests.post(query_url, data=query_parameters, headers=query_headers)
        if find_response.status_code != 200:
            error_msg = f"POST unsuccessful ({find_response.status_code}): {find_response.text}"
            raise Exception(error_msg)

        query_out = find_response.json()
        bindings_out = []
        for binding in query_out["results"]["bindings"]:
            bindings_out.append(binding["i"]["value"].replace(entity_prefix, ''))
        return bindings_out

def get_lexemes(lids: List[str], user_agent=DEFAULT_USER_AGENT) -> Dict[I.Lid, I.LexemeDict]:
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

    return data_output["entities"]
