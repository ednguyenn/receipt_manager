#!/bin/bash

# Variables
BUCKET_NAME="my-receipt-manager-bucket"
REGION="ap-southeast-2"

# Check if the bucket already exists
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'
then
    # Create the S3 bucket
    aws s3api create-bucket \
        --bucket $BUCKET_NAME \
        --region $REGION \
        --create-bucket-configuration LocationConstraint=$REGION

    echo "Bucket '$BUCKET_NAME' created successfully in region '$REGION'."
else
    echo "Bucket '$BUCKET_NAME' already exists."
fi
