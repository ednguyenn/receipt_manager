#!/bin/bash

# Variables
TABLE_NAME="Receipts"

# Check if the table already exists
existing_tables=$(aws dynamodb list-tables --query "TableNames" --output text)

if [[ $existing_tables != *"$TABLE_NAME"* ]]; then
  echo "Table '$TABLE_NAME' does not exist. Creating now..."
  
  # Create the table
  aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions AttributeName=receipt_id,AttributeType=S \
    --key-schema AttributeName=receipt_id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
  
  echo "Table '$TABLE_NAME' created successfully."
else
  echo "Table '$TABLE_NAME' already exists."
fi
