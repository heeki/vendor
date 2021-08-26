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
        self.debug = True
        # aws config
        self.account_id = os.environ.get("ACCOUNT_ID")
        self.role_name = os.environ.get("ROLE_NAME", "vendor")
        self.role_arn = "arn:aws:iam::{}:role/{}".format(self.account_id, self.role_name)
        self.region = os.environ.get("REGION")
        self.service = os.environ.get("SERVICE")
        # aws sessions
        session = boto3.session.Session() if "AWS_LAMBDA_FUNCTION_NAME" in os.environ else boto3.session.Session(profile_name=self.role_name)
        client = session.client("sts")
        response = client.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName="vendor_session"
        )
        self.aws_access_key_id = response["Credentials"]["AccessKeyId"]
        self.aws_secret_access_key = response["Credentials"]["SecretAccessKey"]
        self.aws_session_token = response["Credentials"]["SessionToken"]
        assumed = boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region
        )
        # app credentials
        client = assumed.client("secretsmanager")
        self.auth_grant_type = "refresh_token"
        self.auth_refresh_token = self._get_secret(client, "/vendor/refresh_token")
        self.auth_app_id = self._get_secret(client, "/vendor/app_id")
        self.auth_client_id = self._get_secret(client, "/vendor/client_id")
        self.auth_client_secret = self._get_secret(client, "/vendor/client_secret")
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

    def request(self, url, params):
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
            "region": self.region,
            "service": self.service
        })) if self.debug else None
        auth = AWS4Auth(self.aws_access_key_id, self.aws_secret_access_key, self.region, self.service, session_token=self.aws_session_token)

        # send request
        response = requests.get(url, params=params, headers=headers, auth=auth)
        return response.text
