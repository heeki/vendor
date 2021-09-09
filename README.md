## Overview
This repository comprises code for interacting with the Selling Partner APIs which is documented [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

## Requestor Library
Shared libraries are located in `src/lib`.
* The `encoders.py` file includes encoders for simple json serialization of custom classes.
* The `requestor.py` file includes a class that wraps functionality for making requests to the SPDS endpoints, which requires use of AWS SigV4 signatures.

To leverage the `Requestor` library, perform the following:

1. Import the library.

```python
from lib.requestor import Requestor
```

2. Set the appropriate environment variables wherever the code is being executed. Note that this can be defined in `etc/envvars_vendor.sh` as noted in the environment section below.

```bash
export REQUESTOR_ROLE=[arn_of_spds_iam_role]
export REQUESTOR_REGION=us-east-1
export REQUESTOR_SERVICE=execute-api
export VENDOR_TABLE=[name_of_ddb_table]
```

3. Instantiate an object and make the request call.

```python
r = Requestor()
response = r.request(url, params)
```

The return response is the `requests.Response` object as documented [here](https://docs.python-requests.org/en/latest/api/#requests.Response).


## Environment
A `makefile` has been created to encapsulate all of the commands required for testing and deploying the resources. The makefile expects the following information to be defined in the following files:

`etc/envvars_aws.sh`

```bash
S3BUCKET=[your_s3_bucket]
PROFILE=[your_aws_cli_profile]

P_REFRESH_TOKEN=[refresh_token]
P_APP_ID=[app_id]
P_CLIENT_ID=[client_id]
P_CLIENT_SECRET=[client_secret]

SECRETS_STACK=idl-secrets
SECRETS_TEMPLATE=iac/secrets.yaml
SECRETS_OUTPUT=iac/secrets_output.yaml
SECRETS_PARAMS="ParameterKey=pRefreshToken,ParameterValue=${P_REFRESH_TOKEN} ParameterKey=pAppId,ParameterValue=${P_APP_ID} ParameterKey=pClientId,ParameterValue=${P_CLIENT_ID} ParameterKey=pClientSecret,ParameterValue=${P_CLIENT_SECRET}"

P_NAME="placeholder"

DDB_STACK=idl-vendor-database
DDB_TEMPLATE=iac/dynamodb.yaml
DDB_OUTPUT=iac/dynamodb_output.yaml
DDB_PARAMS="ParameterKey=pName,ParameterValue=${P_NAME}"

P_VENDOR_TABLE=[table_name]

SHARED_STACK=idl-shared
SHARED_TEMPLATE=iac/shared.yaml
SHARED_OUTPUT=iac/shared_output.yaml
SHARED_PARAMS="ParameterKey=pName,ParameterValue=${P_NAME}"

P_API_STAGE=dev
P_PVERSION=1.0
P_REQUESTOR_ROLE=[arn_of_vendor_central_role]
P_REQUESTOR_LAYER=[arn_of_requestor_layer]

APIGW_STACK=idl-vendor-api
APIGW_TEMPLATE=iac/apigw.yaml
APIGW_OUTPUT=iac/apigw_output.yaml
APIGW_PARAMS="ParameterKey=pApiStage,ParameterValue=${P_API_STAGE} ParameterKey=pPayloadVersion,ParameterValue=${P_PVERSION} ParameterKey=pVendorTable,ParameterValue=${P_VENDOR_TABLE} ParameterKey=pRequestorRole,ParameterValue=${P_REQUESTOR_ROLE} ParameterKey=pRequestorLayer,ParameterValue=${P_REQUESTOR_LAYER}"

P_FN_VENDOR=[arn_of_created_function]
P_API_ENDPOINT=[url_of_created_api_endpoint]
```

`etc/envvars_vendor.sh`

```bash
export REQUESTOR_ROLE=[arn_of_spds_iam_role]
export REQUESTOR_REGION=us-east-1
export REQUESTOR_SERVICE=execute-api
export VENDOR_TABLE=[name_of_ddb_table]
```

## Execution
With those environment files configured, you can then execute the commands found in the `makefile`.

To execute the APIs locally, execute the following commands. Note that to run `make vendor.test`, you will need to source an appropriately configured `etc/envvars_vendor.sh`.

* `make vendor.live`: makes a live call to the SPDS API locally
* `make vendor.mock`: makes a mock call to test functionality
* `make vendor.test`: runs local unit tests

To deploy the CloudFormation resources in your AWS account, execute the following commands.

* `make secrets`: creates a stack for Secrets Manager
* `make ddb`: creates a stack for DynamoDB
* `make shared`: creates a stack for shared code in Lambda layers
* `make cognito`: creates a stack for Cognito for auth
* `make apigw`: creates a stack for a REST API on API Gateway

## Making API calls
With Cognito in place, the id token from Cognito must be included as the `Authorization` header in the API requests. The `var/cognito_user.sh` helper script will retrieve the auth tokens from Cognito and set an environment variable `P_AUTH_IDTOKEN` with the value of the id token. Then `make apigw.curl.post.2` can be used to make an authorized call to the API.
