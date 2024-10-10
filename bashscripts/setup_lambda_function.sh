#!/bin/bash

# Define Variables
LAMBDA_FUNCTION_NAME="ReceiptProcessorFunction"      # Your Lambda function name
ROLE_NAME="ReceiptProcessorRole"                     # Name of your IAM role
S3_BUCKET_NAME="my-receipt-manager-bucket"           # Your S3 bucket name
LAMBDA_HANDLER="lambda_function.lambda_handler"      # The handler function in lambda_function.py
DYNAMODB_TABLE="Receipts"                            # Your DynamoDB table name
LAMBDA_RUNTIME="python3.11"                          # Lambda runtime version
LAMBDA_REGION="ap-southeast-2"                       # AWS region
ZIP_FILE_NAME="lambda_function.zip"                  # Name of the deployment ZIP file
PACKAGE_DIR="lambda_package"                         # Directory to hold the Lambda package files

# Step 1: Create IAM Role for Lambda (if it doesn't exist)
echo "Creating IAM Role for Lambda function..."

ROLE_ARN=$(aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }' \
  --query 'Role.Arn' \
  --output text 2>&1)

# Check if the role creation was successful
if [[ $? -ne 0 ]]; then
  # If role already exists, capture the existing role's ARN
  echo "IAM role creation failed or role already exists. Trying to fetch existing role ARN..."
  ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text 2>/dev/null)
  if [[ $? -ne 0 ]]; then
    echo "Error creating or fetching IAM role. Exiting..."
    exit 1
  else
    echo "IAM Role already exists. Using existing role ARN: $ROLE_ARN"
  fi
else
  echo "IAM Role created successfully with ARN: $ROLE_ARN"
fi

# Step 2: Attach Policies to the IAM Role
echo "Attaching policies to the IAM Role..."
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonTextractFullAccess
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Step 3: Wait for the IAM role to be ready
echo "Waiting for IAM role to be ready..."
sleep 20  

# Step 4: Create Lambda Deployment Package
echo "Creating Lambda deployment package..."
mkdir -p $PACKAGE_DIR
cp lambda_function.py $PACKAGE_DIR/
cd $PACKAGE_DIR
zip -r ../$ZIP_FILE_NAME .
cd ..

# Step 5: Create or Update the Lambda Function
echo "Creating or updating Lambda function with role ARN: $ROLE_ARN"
CREATE_RESPONSE=$(aws lambda create-function \
  --function-name $LAMBDA_FUNCTION_NAME \
  --runtime $LAMBDA_RUNTIME \
  --role $ROLE_ARN \
  --handler $LAMBDA_HANDLER \
  --zip-file fileb://$ZIP_FILE_NAME \
  --timeout 120 \
  --memory-size 512 \
  --region $LAMBDA_REGION \
  --environment Variables="{DYNAMODB_TABLE=$DYNAMODB_TABLE,S3_BUCKET_NAME=$S3_BUCKET_NAME}" \
  2>&1)

# Check if the Lambda function was created successfully
if echo "$CREATE_RESPONSE" | grep -q "Function already exist"; then
  echo "Lambda function already exists. Updating the function code..."
  aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://$ZIP_FILE_NAME \
    --region $LAMBDA_REGION
elif echo "$CREATE_RESPONSE" | grep -q "error"; then
  echo "Error creating Lambda function: $CREATE_RESPONSE"
  exit 1
else
  echo "Lambda function created successfully."
fi

# Step 6: Set up S3 Bucket Trigger
echo "Setting up S3 bucket trigger for Lambda function..."
aws lambda add-permission \
  --function-name $LAMBDA_FUNCTION_NAME \
  --principal s3.amazonaws.com \
  --statement-id S3InvokeLambdaPermission \
  --action "lambda:InvokeFunction" \
  --source-arn arn:aws:s3:::$S3_BUCKET_NAME \
  --source-account $(aws sts get-caller-identity --query Account --output text) 2>/dev/null

aws s3api put-bucket-notification-configuration \
  --bucket $S3_BUCKET_NAME \
  --notification-configuration '{
      "LambdaFunctionConfigurations": [
        {
          "LambdaFunctionArn": "arn:aws:lambda:'"$LAMBDA_REGION"':'"$(aws sts get-caller-identity --query Account --output text)"':function:'"$LAMBDA_FUNCTION_NAME"'",
          "Events": ["s3:ObjectCreated:*"],
          "Filter": {
            "Key": {
              "FilterRules": [
                {
                  "Name": "suffix",
                  "Value": ".jpg"
                }
              ]
            }
          }
        }
      ]
    }' 2>/dev/null

echo "Deployment completed successfully."
