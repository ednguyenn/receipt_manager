# backend/aws_config.py

import boto3
import os

def get_aws_client(service_name):
    """
    Initializes and returns a boto3 client for the specified AWS service.
    """
    region = os.environ.get('AWS_REGION', 'us-east-1')
    return boto3.client(service_name, region_name=region)

def get_aws_resource(service_name):
    """
    Initializes and returns a boto3 resource for the specified AWS service.
    """
    region = os.environ.get('AWS_REGION', 'us-east-1')
    return boto3.resource(service_name, region_name=region)
