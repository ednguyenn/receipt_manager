#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
else
  echo ".env file not found. Make sure it exists and is ignored by .gitignore."
  exit 1
fi

# Configuration
REGION="ap-southeast-2"

# Ensure environment variables are loaded
if [ -z "$OPENAI_API_KEY" ] || [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "Missing required environment variables. Please check your .env file."
  exit 1
fi

# Function to create or update secrets in AWS Secrets Manager
create_or_update_secret() {
  local secret_name=$1
  local secret_value=$2

  # Check if secret exists
  SECRET_EXISTS=$(aws secretsmanager describe-secret --secret-id "$secret_name" --region "$REGION" 2>&1)

  if echo "$SECRET_EXISTS" | grep -q 'ResourceNotFoundException'; then
    # Create the secret if it doesn't exist
    echo "Creating secret: $secret_name"
    aws secretsmanager create-secret \
      --name "$secret_name" \
      --secret-string "$secret_value" \
      --region "$REGION"
  else
    # Update the secret if it already exists
    echo "Updating secret: $secret_name"
    aws secretsmanager put-secret-value \
      --secret-id "$secret_name" \
      --secret-string "$secret_value" \
      --region "$REGION"
  fi
}

# Store the secrets
create_or_update_secret "OPENAI_API_KEY" "$OPENAI_API_KEY"
create_or_update_secret "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID"
create_or_update_secret "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY"

echo "Secrets stored/updated successfully."
