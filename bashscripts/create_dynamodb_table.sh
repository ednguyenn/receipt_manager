#!/bin/bash

# Variables
TABLE_NAME="Receipts"
REGION="ap-southeast-2" 

# Check if the table already exists
existing_tables=$(aws dynamodb list-tables --region $REGION --query "TableNames" --output text)

if [[ $existing_tables != *"$TABLE_NAME"* ]]; then
  echo "Table '$TABLE_NAME' does not exist. Creating now..."
  
  # Create the table
  create_table_output=$(aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions AttributeName=receipt_id,AttributeType=S \
    --key-schema AttributeName=receipt_id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION \
    2>&1)  # Capture both stdout and stderr

  # Check if the table creation command succeeded
  if [ $? -eq 0 ]; then
    echo "Table '$TABLE_NAME' created successfully."
  else
    echo "Failed to create table '$TABLE_NAME'. Error:"
    echo "$create_table_output"
    exit 1  # Exit with error code 1 if table creation failed
  fi
else
  echo "Table '$TABLE_NAME' already exists."
fi