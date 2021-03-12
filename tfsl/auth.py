import json
import logging
import time
import requests

import tfsl.utils

from getpass import getpass
from typing import Any, Dict, Optional

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

class WikibaseSession:
    """Auth library for Wikibases.
    """
    def __init__(self,
        username,
        password: Optional[str] = None,
        token: Optional[str] = None,
        auth: Optional[str] = None,
        user_agent: str = 'tfsl 0.0.1',
        URL: str = "https://www.wikidata.org/w/api.php"
    ):
        self.URL = URL
        self.user_agent = user_agent
        self.auth = auth
        self.headers = {"User-Agent": user_agent}
        self.S = requests.Session()

        self.username = username
        self.assertUser = None
        if password is not None:
            self._password = password
        else:
            self._password = getpass(f"Enter password for {self.username}: ")

        DATA = self.get(token_request_params)
        LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]

        connection_request_params = {
            "action": "login",
            "format": "json",
            "lgname": self.username,
            "lgpassword": self._password,
            "lgtoken": LOGIN_TOKEN,
        }
        DATA = self.post(connection_request_params, 30)
        if DATA.get("login", []).get("result") != "Success":
            raise PermissionError("Login failed", DATA["login"]["reason"])
        logging.info("Log in succeeded")

        if token is not None:
            self.CSRF_TOKEN = token
            logging.info("Using CSRF token: %s", self.CSRF_TOKEN)
        else:
            DATA = self.get(csrf_token_params)
            self.CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]
            logging.info("Got CSRF token: %s", self.CSRF_TOKEN)

        if username is not None:
            # truncate bot name if a "bot password" is used
            self.assertUser = username.split("@")[0]

    def push(self, obj_in, summary = None, maxlag_in = maxlag) -> Any:
        """Post data to Wikibase.
        """
        data = obj_in.__jsonout__()
        requestjson = {"action": "wbeditentity", "format": "json"}

        if not data.get("id", False):
            if(data.get("lexicalCategory", False)):
                requestjson["new"] = "lexeme"
            elif(data.get("glosses", False)):
                requestjson["new"] = "sense"
            elif(data.get("representations", False)):
                requestjson["new"] = "form"
            elif(data.get("labels", False) and data.get("sitelinks", False)):
                requestjson["new"] = "item"
            else:
                requestjson["new"] = "property"

        if summary is not None:
            requestjson["summary"] = summary

        requestjson["token"] = self.CSRF_TOKEN

        data = obj_in.__jsonout__()
        requestjson["data"] = json.dumps(data)

        requestjson["assertuser"] = self.assertUser

        requestjson["maxlag"] = str(maxlag_in)

        print(requestjson)

        R = self.S.post(self.URL, data=requestjson, headers=self.headers, auth=self.auth)
        if R.status_code != 200:
            raise Exception("POST was unsuccessfull ({}): {}".format(R.status_code, R.text))

        DATA = R.json()
        if "error" in DATA:
            if DATA["error"]["code"] == "maxlag":
                sleepfor = float(R.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.post(data)
            else:
                raise PermissionError("API returned error: " + str(DATA["error"]))

        logging.debug("Post request succeed")
        return DATA

    def post(self, data: Dict[str, str], maxlag_in = maxlag) -> Any:
        """Post data to Wikibase. The CSRF token is automatically
        filled in if __AUTO__ is given instead.

        :param data: Parameters to send via POST
        :type  data: Dict[str, str])
        :returns: Answer form the server as Objekt
        :rtype: Any

        """
        if data.get("token") == "__AUTO__":
            data["token"] = self.CSRF_TOKEN
        if "assertuser" not in data and self.assertUser is not None:
            data["assertuser"] = self.assertUser
        data["maxlag"] = str(maxlag_in)

        R = self.S.post(self.URL, data=data, headers=self.headers, auth=self.auth)
        if R.status_code != 200:
            raise Exception("POST was unsuccessfull ({}): {}".format(R.status_code, R.text))

        DATA = R.json()
        if "error" in DATA:
            if DATA["error"]["code"] == "maxlag":
                sleepfor = float(R.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.post(data)
            else:
                raise PermissionError("API returned error: " + str(DATA["error"]))

        logging.debug("Post request succeed")
        return DATA

    def get(self, data: Dict[str, str]) -> Any:
        """Send a GET request to wikidata

        :param data: Parameters to send via GET
        :type  data: Dict[str, str]
        :returns: Answer form the server as Objekt
        :rtype: Any

        """
        R = self.S.get(self.URL, params=data, headers=self.headers)
        DATA = R.json()
        if R.status_code != 200 or "error" in DATA:
            # We do not set maxlag for GET requests – so this error can only
            # occur if the users sets maxlag in the request data object
            if DATA["error"]["code"] == "maxlag":
                sleepfor = float(R.headers.get("retry-after", 5))
                logging.info("Maxlag hit, waiting for %.1f seconds", sleepfor)
                time.sleep(sleepfor)
                return self.get(data)
            else:
                raise Exception(
                    "GET was unsuccessfull ({}): {}".format(R.status_code, R.text)
                )
        logging.debug("Get request succeed")
        return DATA
