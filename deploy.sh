cd src
zip -r ../source_code.zip *
cd ..
aws s3 cp source_code.zip s3://surpluscapitalpythonlambda
aws lambda update-function-code \
  --function-name SurplusCapitalPythonLambda \
  --s3-bucket surpluscapitalpythonlambda \
  --s3-key source_code.zip