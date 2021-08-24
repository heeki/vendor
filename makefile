include etc/environment.sh

api.ec2:
	aws --profile 1527 sts get-session-token --duration-seconds 900 | jq '{"aws_access_key_id": .Credentials.AccessKeyId, "aws_secret_access_key": .Credentials.SecretAccessKey, "aws_session_token": .Credentials.SessionToken}' > etc/session.json
	python src/execute.py --type ec2
api.vendor:
	aws --profile vendor sts get-session-token --duration-seconds 900 | jq '{"aws_access_key_id": .Credentials.AccessKeyId, "aws_secret_access_key": .Credentials.SecretAccessKey, "aws_session_token": .Credentials.SessionToken}' > etc/session.json
	python src/execute.py --type vendor | jq
