import argparse
import json
from datetime import datetime
from lib.requestor import Requestor

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, help="ec2|vendor")
    args = ap.parse_args()

    # TODO: move these to environment variables
    with open("etc/config_{}.json".format(args.type)) as f:
        config = json.load(f)
        if args.type == "vendor":
            # ts_before = datetime.now()
            # ts_after = ts_before - timedelta(days=7)
            ts_before = datetime(2019, 9, 21, 0, 0, 0)
            ts_after = datetime(2019, 8, 20, 14, 0, 0)
            config["createdBefore"] = ts_before
            config["createdAfter"] = ts_after
    # TODO: move these to a secure credentials store
    with open("etc/credentials.json") as f:
        creds = json.load(f)
    # TODO: move this to assume role or sts calls
    with open("etc/session.json") as f:
        session = json.load(f)
        for token in session:
            creds[token] = session[token]

    r = Requestor(config, creds)
    response = r.request(config["host"], config["path"], config["method"], config["params"], config["data"])

    if type(response) == dict:
        print(json.dumps(response))
    else:
        print(response.read().decode("utf-8"))

if __name__ == "__main__":
    main()
