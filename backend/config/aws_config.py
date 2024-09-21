import boto3
import json
import os

# Initialize AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb_client = boto3.resource('dynamodb')

# DynamoDB table name (set this in your Lambda environment variables)
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ReceiptsTable')

# Reference to the DynamoDB table
receipts_table = dynamodb_client.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    Lambda function handler to process uploaded receipts.
    """

    # Log the received event for debugging
    print("Received event: " + json.dumps(event, indent=2))

    # Iterate over each record (in case multiple files are uploaded)
    for record in event['Records']:
        # Extract bucket name and object key from the event
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        print(f"Processing file: s3://{bucket_name}/{object_key}")

        # Call Textract to analyze the expense document
        try:
            textract_response = textract_client.analyze_expense(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': object_key
                    }
                }
            )
            print("Textract analysis completed successfully.")
        except Exception as e:
            print(f"Error in Textract analysis: {e}")
            raise e

        # Parse the Textract response to extract relevant data
        extracted_data = parse_textract_response(textract_response)
        print("Extracted Data:", extracted_data)

        # Add additional metadata if needed (e.g., user ID)
        user_id = extract_user_id_from_key(object_key)
        extracted_data['user_id'] = user_id

        # Store the extracted data in DynamoDB
        try:
            receipts_table.put_item(Item=extracted_data)
            print("Data stored in DynamoDB successfully.")
        except Exception as e:
            print(f"Error storing data in DynamoDB: {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Receipt processing completed successfully.')
    }

def parse_textract_response(textract_response):
    """
    Parses the Textract response from analyze_expense API to extract key information.
    """
    extracted_data = {}

    # Loop through each expense document detected by Textract
    for document in textract_response.get('ExpenseDocuments', []):
        # Extract summary fields (e.g., VendorName, TotalAmount)
        for field in document.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text')
            field_value = field.get('ValueDetection', {}).get('Text')

            if field_type and field_value:
                # Normalize the field names if necessary
                normalized_field_name = field_type.replace(" ", "_").lower()
                extracted_data[normalized_field_name] = field_value

        # Optionally extract line items (individual purchased items)
        line_items = []
        for line_item_group in document.get('LineItemGroups', []):
            for line_item in line_item_group.get('LineItems', []):
                item_data = {}
                for item_field in line_item.get('LineItemExpenseFields', []):
                    item_field_type = item_field.get('Type', {}).get('Text')
                    item_field_value = item_field.get('ValueDetection', {}).get('Text')

                    if item_field_type and item_field_value:
                        normalized_item_field_name = item_field_type.replace(" ", "_").lower()
                        item_data[normalized_item_field_name] = item_field_value
                if item_data:
                    line_items.append(item_data)
        if line_items:
            extracted_data['items'] = line_items

    return extracted_data

def extract_user_id_from_key(object_key):
    """
    Extracts the user ID from the S3 object key.
    Assumes the key is in the format 'user_id/filename'.
    """
    try:
        user_id = object_key.split('/')[0]
        return user_id
    except IndexError:
        print("Unable to extract user ID from object key.")
        return 'unknown_user'
