#!/bin/bash
source etc/envvars_aws.sh

OUTPUT3=`aws --profile $PROFILE cognito-idp initiate-auth \
--client-id $P_COGNITO_CLIENTID \
--auth-flow USER_PASSWORD_AUTH \
--auth-parameters USERNAME=${P_COGNITO_USERNAME},PASSWORD=${P_COGNITO_USERPERMPW}`

echo $OUTPUT3 | jq
export P_AUTH_IDTOKEN=$(echo $OUTPUT3 | jq -r '.AuthenticationResult.IdToken')