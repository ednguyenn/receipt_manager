# backend/create_table.py

import boto3
import os
from botocore.exceptions import ClientError

# DynamoDB table name
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ReceiptsTable')

def create_receipts_table():
    """Create a DynamoDB table for storing receipt data."""
    dynamodb = boto3.resource('dynamodb')

    try:
        # Define the table schema
        table = dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'receipt_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'  # String type
                },
                {
                    'AttributeName': 'receipt_id',
                    'AttributeType': 'S'  # String type
                },
                {
                    'AttributeName': 'vendor_name',
                    'AttributeType': 'S'  # String type for querying by vendor name
                },
                {
                    'AttributeName': 'transaction_date',
                    'AttributeType': 'S'  # String type for querying by date
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'VendorNameIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'vendor_name',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'TransactionDateIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'transaction_date',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ]
        )

        print(f"Creating table '{DYNAMODB_TABLE}'...")
        table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMODB_TABLE)
        print(f"Table '{DYNAMODB_TABLE}' created successfully.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table '{DYNAMODB_TABLE}' already exists.")
        else:
            print(f"Error creating table: {e}")
            raise

if __name__ == '__main__':
    create_receipts_table()
