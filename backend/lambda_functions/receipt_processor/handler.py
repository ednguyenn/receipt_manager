# backend/lambda_functions/process_receipt/handler.py

import json
import boto3
import os
from botocore.exceptions import ClientError

# AWS Clients
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'ReceiptsTable')
receipts_table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Extract bucket name and file key from S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    # Call Textract to extract text from the receipt
    response = textract_client.analyze_expense(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': file_key}}
    )

    # Parse Textract response
    extracted_data = parse_textract_response(response)
    extracted_data['file_key'] = file_key

    # Store the data in DynamoDB
    try:
        receipts_table.put_item(Item=extracted_data)
    except ClientError as e:
        print(f"Error storing data in DynamoDB: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Receipt processed successfully.')
    }

def parse_textract_response(response):
    extracted_data = {}
    for doc in response['ExpenseDocuments']:
        for field in doc['SummaryFields']:
            field_type = field['Type']['Text']
            field_value = field.get('ValueDetection', {}).get('Text', '')
            if field_type and field_value:
                extracted_data[field_type.lower().replace(' ', '_')] = field_value

    return extracted_data
