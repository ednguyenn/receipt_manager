# create_table.py

import boto3
import botocore.exceptions
import os

def create_receipts_table(table_name='ReceiptsTable'):
    """
    Creates a DynamoDB table for storing receipt data.
    """
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # Define the table schema
    try:
        table = dynamodb.create_table(
            TableName=table_name,
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
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'receipt_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'vendor_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'transaction_date',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'total_amount',
                    'AttributeType': 'N'
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

        print(f"Creating table '{table_name}'...")
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully.")

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table '{table_name}' already exists.")
        else:
            print(f"Unexpected error: {e}")
            raise

if __name__ == '__main__':
    create_receipts_table()
