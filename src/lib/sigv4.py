import json
import hashlib
import hmac
from datetime import datetime

class Signer:
    def __init__(self, region, service, signed_headers, access_key, secret_key):
        # static data
        self.algorithm = "AWS4-HMAC-SHA256"
        # parameters
        self.region = region
        self.service = service
        self.signed_headers = signed_headers
        self.access_key = access_key
        self.secret_key = secret_key   

    def _get_hmac_digest(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_sha256_digest(self, data):
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _get_signing_key(self, datestamp):
        signing_date = self._get_hmac_digest(("AWS4" + self.secret_key).encode("utf-8"), datestamp)
        signing_region = self._get_hmac_digest(signing_date, self.region)
        signing_service = self._get_hmac_digest(signing_region, self.service)
        signing_key = self._get_hmac_digest(signing_service, "aws4_request")
        return signing_key

    def _stringify(self, data, is_headers=False):
        output = ""
        for datum in data:
            output += "{}\n".format(datum)
        if is_headers:
            return output
        else:
            return output.rstrip("\n")

    def create_signature(self, method, host, path, params, headers, data, now):
        timestamp = now.strftime('%Y%m%dT%H%M%SZ')
        datestamp = now.strftime('%Y%m%d')
        interim = ["{}:{}".format(header, headers[header]) for header in headers]
        canonical_headers = self._stringify(interim, is_headers=True)
        payload_hash = self._get_sha256_digest(data)
        canonical_request = self._stringify([
            method,
            path,
            params,
            canonical_headers,
            self.signed_headers,
            payload_hash
        ])
        signing_key = self._get_signing_key(datestamp)
        credential_scope = "{}/{}/{}/aws4_request".format(datestamp, self.region, self.service)
        string_to_sign = self._stringify([
            self.algorithm,
            timestamp,
            credential_scope,
            self._get_sha256_digest(canonical_request)
        ])
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        header = "{} Credential={}/{}, SignedHeaders={}, Signature={}".format(self.algorithm, self.access_key, credential_scope, self.signed_headers, signature)
        output = {
            "canonical_request": canonical_request,
            "signature": signature,
            "header": header
        }
        return output
