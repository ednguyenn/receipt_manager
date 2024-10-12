#!/bin/bash

# Step 1: Push Docker image to ECR
echo "Pushing Docker image to ECR..."
./bashscripts/push_to_ECR.sh

if [ $? -eq 0 ]; then
  echo "Docker image pushed to ECR successfully."
else
  echo "Failed to push Docker image to ECR."
  exit 1
fi

# Step 2: Store secrets in AWS Secrets Manager
echo "Storing secrets in AWS Secrets Manager..."
./bashscripts/store_secrets.sh

if [ $? -eq 0 ]; then
  echo "Secrets stored successfully."
else
  echo "Failed to store secrets in AWS Secrets Manager."
  exit 1
fi

# Step 3: Register the ECS Task Definition
echo "Registering ECS Task Definition..."
./bashscripts/register_task_definition.sh

if [ $? -eq 0 ]; then
  echo "ECS Task Definition registered successfully."
else
  echo "Failed to register ECS Task Definition."
  exit 1
fi

# Step 4: Set up the infrastructure using CloudFormation
echo "Setting up ECS Service and ALB using CloudFormation..."
./bashscripts/setup_infrastructure.sh

if [ $? -eq 0 ]; then
  echo "ECS Service and ALB deployed successfully."
else
  echo "Failed to deploy ECS Service and ALB."
  exit 1
fi
