include etc/envvars_aws.sh
include etc/envvars_vendor.sh

vendor.execute:
	python src/execute.py --type vendor | jq
vendor.token:
	aws --profile vendor sts get-session-token --duration-seconds 900 | jq '{"aws_access_key_id": .Credentials.AccessKeyId, "aws_secret_access_key": .Credentials.SecretAccessKey, "aws_session_token": .Credentials.SessionToken}'

secrets: secrets.package secrets.deploy
secrets.package:
	sam package -t ${SECRETS_TEMPLATE} --output-template-file ${SECRETS_OUTPUT} --s3-bucket ${S3BUCKET}
secrets.deploy:
	sam deploy -t ${SECRETS_OUTPUT} --stack-name ${SECRETS_STACK} --parameter-overrides ${SECRETS_PARAMS} --capabilities CAPABILITY_NAMED_IAM
