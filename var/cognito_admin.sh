#!/bin/bash
source etc/envvars_aws.sh

OUTPUT1=`aws --profile $PROFILE cognito-idp admin-initiate-auth \
--user-pool-id $P_COGNITO_USERPOOL \
--client-id $P_COGNITO_CLIENTID \
--auth-flow ADMIN_NO_SRP_AUTH \
--auth-parameters USERNAME=${P_COGNITO_USERNAME},PASSWORD=${P_COGNITO_USERTEMPPW}`
export P_COGNITO_SESSION=`echo $OUTPUT1 | jq -r ".Session"`

OUTPUT2=`aws --profile $PROFILE cognito-idp admin-respond-to-auth-challenge \
--user-pool-id $P_COGNITO_USERPOOL \
--client-id $P_COGNITO_CLIENTID \
--challenge-name NEW_PASSWORD_REQUIRED \
--challenge-responses USERNAME=$P_COGNITO_USERNAME,NEW_PASSWORD=$P_COGNITO_USERPERMPW \
--session $P_COGNITO_SESSION`

OUTPUT3=`aws --profile $PROFILE cognito-idp initiate-auth \
--client-id $P_COGNITO_CLIENTID \
--auth-flow USER_PASSWORD_AUTH \
--auth-parameters USERNAME=${P_COGNITO_USERNAME},PASSWORD=${P_COGNITO_USERPERMPW}`

echo $OUTPUT3 | jq