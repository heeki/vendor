import json
import urllib.request
from datetime import datetime, timedelta
from lib.encoders import DateTimeEncoder

config = {}

class Requestor:
    def __init__(self):
        pass

    def get_access_token(self):
        output = ""
        return output

    def request(self, endpoint, path):
        # ts_before = datetime.now()
        # ts_after = ts_before - timedelta(days=7)
        ts_before = datetime(2019, 9, 21, 0, 0, 0)
        ts_after = datetime(2019, 8, 20, 14, 0, 0)
        headers = {
            "host": endpoint,
            "x-amz-access-token": "token",
            "x-amz-date": datetime.now().isoformat(timespec="seconds"),
            "user-agent": "CPGDL/0.1 (Language=Python 3.8.9; Platform=Catalina 10.15.7)"
        }
        payload = {
            "createdBefore": ts_before.isoformat(timespec="seconds"),
            "createdAfter": ts_after.isoformat(timespec="seconds"),
            "includeDetails": True,
            "limit": 2,
            "sortOrder": "DESC"
        }        
        print(json.dumps(payload, cls=DateTimeEncoder))

        qsp = ""
        for pk in payload:
            qsp += "{}={}&".format(pk, payload[pk])
        qsp = qsp[:-1]
        url = "{}/{}?{}".format(endpoint, path, qsp)

        response = {}
        request = urllib.request.Request(url)
        request.method = "GET"
        for header in headers:
            request.add_header(header, headers[header])
        print(url)
        # request.data = json.dumps(payload).encode("utf-8")
        response = urllib.request.urlopen(request)
        return response

def main():
    with open("etc/credentials.json") as f:
        creds = json.load(f)
        print(json.dumps(creds))
    with open("etc/config.json") as f:
        config = json.load(f)
        print(json.dumps(config))
    r = Requestor()
    response = r.request(config["endpoint"], config["path"])
    print(response)

if __name__ == "__main__":
    main()
