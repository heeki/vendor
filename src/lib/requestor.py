import json
import urllib.request
from datetime import datetime, timedelta
from lib.encoders import DateTimeEncoder
from lib.sigv4 import Signer

class Requestor:
    def __init__(self, config, creds):
        # debug
        self.debug = True
        # config
        self.region = config["region"]
        self.service = config["service"]
        self.signed_headers = config["signed_headers"]
        # credentials
        self.auth_grant_type = creds["grant_type"]
        self.auth_refresh_token = creds["refresh_token"]
        self.auth_app_id = creds["app_id"]
        self.auth_client_id = creds["client_id"]
        self.auth_client_secret = creds["client_secret"]
        self.aws_access_key_id = creds["aws_access_key_id"]
        self.aws_secret_access_key = creds["aws_secret_access_key"]
        self.credentials = self._get_access_token()

    def _request(self, url, method="GET", headers=[], data=None):
        response = {
            "url": url,
            "method": method,
            "headers": headers,
            "data": data
        }
        if data is not None:
            request = urllib.request.Request(url, data=data)
        else:
            request = urllib.request.Request(url)
        request.method = method
        for header in headers:
            request.add_header(header, headers[header])
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print(json.dumps({
                "code": e.code,
                "reason": str(e.reason),
                "headers": str(e.headers).rstrip().split("\n")
            })) if self.debug else None
        return response

    def _get_access_token(self):
        url = "https://api.amazon.com/auth/o2/token"
        method = "POST"
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        data = "grant_type={}".format(self.auth_grant_type)
        data += "&refresh_token={}".format(self.auth_refresh_token)
        data += "&client_id={}".format(self.auth_client_id)
        data += "&client_secret={}".format(self.auth_client_secret)
        ts_requested = datetime.now()
        response = self._request(url, method, headers, data.encode("utf-8"))
        credentials = json.loads(response.read().decode("utf-8"))
        ts_expiry = ts_requested + timedelta(seconds=credentials["expires_in"])
        credentials["ts_requested"] = ts_requested
        credentials["ts_expiry"] = ts_expiry
        print(json.dumps(credentials, cls=DateTimeEncoder)) if self.debug else None
        return credentials

    def _construct_headers(self, host, timestamp):
        headers = {
            "host": host,
            # "accept": "application/json",
            "user-agent": "CPGDL/0.1 (Language=Python 3.8.9; Platform=Catalina 10.15.7)",
            "x-amz-access-token": self.credentials["access_token"],
            "x-amz-date": timestamp.strftime('%Y%m%dT%H%M%SZ')
        }
        return headers

    def _construct_params(self, data):
        params = ""
        for pkey in data:
            params += "{}={}&".format(pkey, data[pkey])
        params = params[:-1]
        return params

    def request(self, host, path, method, params, data):
        now = datetime.utcnow()
        headers = self._construct_headers(host, now)
        params = self._construct_params(params)
        signer = Signer(self.region, self.service, self.signed_headers, self.aws_access_key_id, self.aws_secret_access_key)
        signature = signer.create_signature(method, host, path, params, headers, data, now)
        headers["Authorization"] = signature["header"]
        print(json.dumps(headers, cls=DateTimeEncoder)) if self.debug else None
        if path == "/":
            url = "https://{}?{}".format(host, params)
        else:
            url = "https://{}/{}?{}".format(host, path, params)
        response = self._request(url, method=method, headers=headers)
        return response
