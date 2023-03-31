#!/bin/bash

function_exists() {
  local function_name=$1
  aws lambda get-function --function-name "$function_name" > /dev/null 2>&1
}

create_function() {
  local function_name=$1
  local s3_bucket=$2
  local s3_key=$3
  aws lambda create-function \
    --function-name "$function_name" \
    --runtime python3.8 \
    --role YOUR_EXECUTION_ROLE_ARN \
    --handler YOUR_HANDLER_NAME \
    --code "S3Bucket=$s3_bucket,S3Key=$s3_key"
}

deploy_function() {
  local function_name=$1
  local s3_folder=$2
  cd src
  zip -r ../source_code.zip *
  cd ..
  aws s3 cp source_code.zip "s3://surpluscapitalpythonlambda/$s3_folder/"
  
  if function_exists "$function_name"; then
    aws lambda update-function-code \
      --function-name "$function_name" \
      --s3-bucket surpluscapitalpythonlambda \
      --s3-key "$s3_folder/source_code.zip"
  else
    create_function "$function_name" surpluscapitalpythonlambda "$s3_folder/source_code.zip"
  fi
}

if [[ $1 == "--prod" ]]; then
  deploy_function "SurplusCapitalPythonLambdaProd" "prod"
else
  deploy_function "SurplusCapitalPythonLambdaDev" "dev"
fi