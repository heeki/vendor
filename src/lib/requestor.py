import boto3
import json
import os
import requests
# from datetime import datetime, timedelta
from lib.encoders import DateTimeEncoder
from requests_aws4auth import AWS4Auth

class Requestor:
    def __init__(self):
        # debug
        self.debug = False
        # aws config
        self.requestor_role = os.environ.get("REQUESTOR_ROLE")
        self.requestor_region = os.environ.get("REQUESTOR_REGION")
        self.requestor_service = os.environ.get("REQUESTOR_SERVICE")
        self.aws_region = os.environ.get("AWS_REGION", self.requestor_region)
        # aws sessions
        profile = self.requestor_role.split("/")[1]
        session = boto3.session.Session() if "AWS_LAMBDA_FUNCTION_NAME" in os.environ else boto3.session.Session(profile_name=profile)
        client = session.client("sts")
        response = client.assume_role(
            RoleArn=self.requestor_role,
            RoleSessionName="vendor_session"
        )
        self.aws_access_key_id = response["Credentials"]["AccessKeyId"]
        self.aws_secret_access_key = response["Credentials"]["SecretAccessKey"]
        self.aws_session_token = response["Credentials"]["SessionToken"]
        assumed = boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.aws_region
        )
        # app credentials
        client = assumed.client("secretsmanager")
        self.auth_grant_type = "refresh_token"
        self.auth_refresh_token = self._get_secret(client, "/idl/refresh_token")
        self.auth_app_id = self._get_secret(client, "/idl/app_id")
        self.auth_client_id = self._get_secret(client, "/idl/client_id")
        self.auth_client_secret = self._get_secret(client, "/idl/client_secret")
        self.auth_credentials = self._get_access_token()

    def _get_secret(self, client, secret_id):
        response = client.get_secret_value(
            SecretId=secret_id
        )
        return response["SecretString"]

    def _get_access_token(self):
        url = "https://api.amazon.com/auth/o2/token"
        headers = {
            "content-type": "application/json"
        }
        data = json.dumps({
            "grant_type": self.auth_grant_type,
            "refresh_token": self.auth_refresh_token,
            "client_id": self.auth_client_id,
            "client_secret": self.auth_client_secret
        }).encode("utf-8")        
        response = requests.post(url, headers=headers, data=data)
        credentials = json.loads(response.text)
        print(json.dumps(credentials, cls=DateTimeEncoder)) if self.debug else None
        return credentials

    def refresh_access_token(self):
        """ for use when access token has expired and endpoint is returning a 403 error
        """
        self.auth_credentials = self._get_access_token()

    def request(self, url, method="GET", params=None, data=None):
        """ generic request method for making sigv4 authenticated api requests
        arguments:
        - url: request endpoint
        - method: rest method, e.g. GET, POST, PUT, DELETE
        - params: needed only with GET
        - data: needed only with POST, PUT, DELETE
        """
        # configure headers
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": "CPGDL/0.1 (Language=Python 3.8.9; Platform=Catalina 10.15.7)",
            # "x-amz-date": datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            "x-amz-access-token": self.auth_credentials["access_token"]
        }
        print(json.dumps(headers, cls=DateTimeEncoder)) if self.debug else None

        # configure auth
        print(json.dumps({
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
            "aws_session_token": self.aws_session_token,
            "requestor_region": self.requestor_region,
            "requestor_service": self.requestor_service
        })) if self.debug else None
        auth = AWS4Auth(self.aws_access_key_id, self.aws_secret_access_key, self.requestor_region, self.requestor_service, session_token=self.aws_session_token)

        # send request
        if method == "GET" and params is not None:
            response = requests.get(url, params=params, headers=headers, auth=auth)
        if method == "POST" and data is not None:
            response = requests.post(url, headers=headers, auth=auth, data=data)
        elif method == "PUT" and data is not None:
            response = requests.put(url, headers=headers, auth=auth, data=data)
        elif method == "DELETE" and data is not None:
            response = requests.delete(url, headers=headers, auth=auth, data=data)
        else:
            response = None

        return response
