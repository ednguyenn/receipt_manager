#!/bin/bash

# Variables 
AWS_REGION="ap-southeast-2"                       
REPOSITORY_NAME="receipt_manager-server"                 
IMAGE_TAG="latest"                            
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text) # Automatically fetches your AWS Account ID

# ECR repository URL
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:${IMAGE_TAG}"

# Step 1: Authenticate Docker to your Amazon ECR registry
echo "Authenticating Docker to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

if [ $? -ne 0 ]; then
  echo "Docker login failed. Please check your AWS credentials and try again."
  exit 1
fi

# Step 2: Build the Docker image using docker-compose
echo "Building the Docker image using docker-compose..."
docker compose up --build -d

if [ $? -ne 0 ]; then
  echo "Docker compose build failed. Please check your docker-compose.yml file and try again."
  exit 1
fi

# Step 3: Tag the Docker image
echo "Tagging the Docker image..."
docker tag ${REPOSITORY_NAME}:${IMAGE_TAG} ${ECR_REPOSITORY_URI}

if [ $? -ne 0 ]; then
  echo "Failed to tag the Docker image. Please check the image name and tag."
  exit 1
fi
# Step 4: Check if the ECR repository exists, and create it if not.
if ! aws ecr describe-repositories --repository-names ${REPOSITORY_NAME} --region ${AWS_REGION} > /dev/null 2>&1; then
    echo "ECR repository ${REPOSITORY_NAME} does not exist. Creating..."
    aws ecr create-repository --repository-name ${REPOSITORY_NAME} --region ${AWS_REGION}
    echo "ECR repository ${REPOSITORY_NAME} created successfully."
fi

# Step 5: Push the Docker image to ECR
echo "Pushing the Docker image to ECR..."
docker push ${ECR_REPOSITORY_URI}

if [ $? -ne 0 ]; then
  echo "Failed to push the Docker image to ECR. Please check the repository URI and try again."
  exit 1
fi

# Step 5: Stop the Docker Compose services 
echo "Stopping Docker Compose services..."
docker compose down

# Success message
echo "Docker image has been successfully built and pushed to ECR: ${ECR_REPOSITORY_URI}"
