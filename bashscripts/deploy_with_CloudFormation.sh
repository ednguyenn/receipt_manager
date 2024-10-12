#!/bin/bash

# Configuration
STACK_NAME="receipt-manager-stack"
TEMPLATE_FILE="cloudformation/ecs_deployment_template.json"
REGION="ap-southeast-2"

# Deploy the CloudFormation stack
echo "Deploying CloudFormation stack: $STACK_NAME"

aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Wait for stack creation to complete
echo "Waiting for stack creation to complete..."

aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $REGION

if [ $? -eq 0 ]; then
  echo "Stack created successfully!"
else
  echo "Error: Stack creation failed."
  exit 1
fi
