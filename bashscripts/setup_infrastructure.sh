#!/bin/bash

# Configuration
STACK_NAME="receipt-manager-ecs-service-stack"
TEMPLATE_FILE="cloudformation/ecs_service_with_alb.json"
REGION="ap-southeast-2"

# Deploy the CloudFormation stack
echo "Deploying ECS Service CloudFormation stack..."
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://$TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION \
  --parameters ParameterKey=ECSClusterName,ParameterValue=my-first-cluster \
               ParameterKey=ECSServiceName,ParameterValue=webapp \
               ParameterKey=VpcID,ParameterValue=vpc-0f501f8639f96856f \
               ParameterKey=SubnetIDs,ParameterValue="subnet-090e88f0d541ac21d,subnet-01bb6a97d29ecf083,subnet-03b7be7c8ddb57f0e"

# Wait for the stack creation to complete
echo "Waiting for CloudFormation stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION

if [ $? -eq 0 ]; then
  echo "ECS Service with ALB deployed successfully!"
  # Output the ALB DNS name
  aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
    --output text --region $REGION
else
  echo "ECS Service with ALB deployment failed."
  exit 1
fi
