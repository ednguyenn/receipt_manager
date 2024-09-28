import boto3
import json
import os
import openai
import requests

# Initialize the necessary AWS clients
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Receipts')

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def lambda_handler(event, context):
    # Get bucket and object key from S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Call Textract to extract text from the uploaded receipt image
    textract_response = textract.analyze_document(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': object_key}},
        FeatureTypes=["FORMS", "TABLES"]
    )
    
    # Extract raw text from the Textract response
    raw_text = extract_raw_text(textract_response)
    
    # Send the raw text to the OpenAI API for structured data extraction
    extracted_data = extract_relevant_data(raw_text)
    
    # Store extracted data in DynamoDB
    receipt_id = object_key.split('/')[-1].split('.')[0]  # Derive receipt ID from S3 object key
    table.put_item(
        Item={
            'receipt_id': receipt_id,
            'merchant': extracted_data['merchant'],
            'receipt_date': extracted_data['date'],
            'amount': extracted_data['amount'],
            's3_url': f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Receipt processed successfully!')
    }

def extract_raw_text(textract_response):
    """
    Extract raw text from Textract response. The raw text will be sent to the OpenAI API.
    """
    raw_text = ""
    for block in textract_response['Blocks']:
        if block['BlockType'] == 'LINE':
            raw_text += block['Text'] + "\n"
    return raw_text

def extract_relevant_data(raw_text):
    """
    Send the extracted text to the OpenAI API for structured data extraction.
    """
    prompt = f"""
    You are a data extraction system. I will provide you with raw text extracted from a receipt, and you need to return the merchant name, date of the transaction, and total amount in JSON format. If any information is missing, leave it empty.

    Here is the text from the receipt:

    "{raw_text}"

    Please extract the information and return the result in this JSON format:

    {{
        "merchant": "",
        "date": "",
        "amount": ""
    }}

    Only return valid and correctly formatted data. Do not include any additional information.
    """

    try:
        # Call OpenAI API to get the structured response
        response = openai.Completion.create(
            engine="gpt-3.5-turbo", 
            prompt=prompt,
            max_tokens=150,
            temperature=0.0
        )
        
        # Extract the response text and convert it to a Python dictionary (JSON)
        extracted_data = json.loads(response['choices'][0]['text'].strip())
        return extracted_data
    
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return {
            "merchant": "",
            "date": "",
            "amount": ""
        }