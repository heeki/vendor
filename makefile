include etc/envvars_aws.sh
include etc/envvars_vendor.sh

vendor.live:
	python src/execute.py --type live | jq
vendor.mock:
	python src/execute.py --type mock | jq
vendor.test:
	python src/test.py
vendor.token:
	aws --profile vendor sts get-session-token --duration-seconds 900 | jq '{"aws_access_key_id": .Credentials.AccessKeyId, "aws_secret_access_key": .Credentials.SecretAccessKey, "aws_session_token": .Credentials.SessionToken}'

secrets: secrets.package secrets.deploy
secrets.package:
	sam package -t ${SECRETS_TEMPLATE} --output-template-file ${SECRETS_OUTPUT} --s3-bucket ${S3BUCKET}
secrets.deploy:
	sam deploy -t ${SECRETS_OUTPUT} --stack-name ${SECRETS_STACK} --parameter-overrides ${SECRETS_PARAMS} --capabilities CAPABILITY_NAMED_IAM

ddb: ddb.package ddb.deploy
ddb.package:
	sam package -t ${DDB_TEMPLATE} --output-template-file ${DDB_OUTPUT} --s3-bucket ${S3BUCKET}
ddb.deploy:
	sam deploy -t ${DDB_OUTPUT} --stack-name ${DDB_STACK} --parameter-overrides ${DDB_PARAMS} --capabilities CAPABILITY_NAMED_IAM

shared: shared.package shared.deploy
shared.package:
	rm -rf build
	mkdir -p build/python/lib && rsync -av --delete --exclude src/lib/__pycache__ src/lib/* build/python/lib
	pip install -r requirements.txt -t build/python
	sam package -t ${SHARED_TEMPLATE} --output-template-file ${SHARED_OUTPUT} --s3-bucket ${S3BUCKET}
shared.deploy:
	sam deploy -t ${SHARED_OUTPUT} --stack-name ${SHARED_STACK} --parameter-overrides ${SHARED_PARAMS} --capabilities CAPABILITY_NAMED_IAM

cognito: cognito.package cognito.deploy
cognito.package:
	sam package -t ${COGNITO_TEMPLATE} --output-template-file ${COGNITO_OUTPUT} --s3-bucket ${S3BUCKET}
cognito.deploy:
	sam deploy -t ${COGNITO_OUTPUT} --stack-name ${COGNITO_STACK} --parameter-overrides ${COGNITO_PARAMS} --capabilities CAPABILITY_NAMED_IAM

apigw: apigw.package apigw.deploy
apigw.package:
	sam package -t ${APIGW_TEMPLATE} --output-template-file ${APIGW_OUTPUT} --s3-bucket ${S3BUCKET}
apigw.deploy:
	sam deploy -t ${APIGW_OUTPUT} --stack-name ${APIGW_STACK} --parameter-overrides ${APIGW_PARAMS} --capabilities CAPABILITY_NAMED_IAM
apigw.local.invoke:
	sam local invoke -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/local_envvars.json -e etc/local_event_api_get.json FnVendor | jq
apigw.local.api:
	sam local start-api -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/local_envvars.json
apigw.local.curl.get:
	curl -s -XGET http://127.0.0.1:3000/vendor | jq
apigw.local.curl.post:
	curl -s -XPOST -d @etc/local_event.json http://127.0.0.1:3000/vendor | jq
apigw.invoke:
	aws --profile ${PROFILE} lambda invoke --function-name ${P_FN_VENDOR} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode
	cat tmp/fn.json | jq
apigw.curl.post.1:
	curl -s -XPOST -d @etc/local_event.json ${P_API_ENDPOINT} | jq
apigw.curl.post.2:
	curl -s -XPOST -d @etc/local_event.json -H "Authorization: ${P_AUTH_IDTOKEN}" ${P_API_ENDPOINT} | jq