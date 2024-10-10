#!/bin/bash

# Variables
CLUSTER_NAME="my-ecs-cluster"
REGION="ap-southeast-2"

# Create ECS Cluster
echo "Creating ECS Cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION

if [ $? -eq 0 ]; then
  echo "ECS Cluster '$CLUSTER_NAME' created successfully!"
else
  echo "Failed to create ECS Cluster."
  exit 1
fi
