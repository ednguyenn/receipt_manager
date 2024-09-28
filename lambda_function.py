import boto3
import json
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file if running locally (optional)
load_dotenv()

# Initialize the necessary AWS clients
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Receipts')

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def lambda_handler(event, context):
    try:
        # Step 1: Get the bucket and object key from the S3 event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        print(f"Processing file from bucket: {bucket_name}, key: {object_key}")

        # Step 2: Call Textract to extract text from the uploaded receipt image
        textract_response = textract.analyze_document(
            Document={'S3Object': {'Bucket': bucket_name, 'Name': object_key}},
            FeatureTypes=["FORMS", "TABLES"]
        )
        print(f"Textract response received: {textract_response}")

        # Check if Textract returned valid data
        if 'Blocks' not in textract_response or not textract_response['Blocks']:
            print("Error: Textract did not return any text blocks.")
            return {
                'statusCode': 400,
                'body': json.dumps('Error: Textract did not return any text blocks.')
            }

        # Step 3: Extract raw text from the Textract response
        raw_text = extract_raw_text(textract_response)
        print(f"Extracted raw text: {raw_text}")

        # Check if raw_text is empty
        if not raw_text:
            print("Error: No text found in Textract response.")
            return {
                'statusCode': 400,
                'body': json.dumps('Error: No text found in Textract response.')
            }

        # Step 4: Send the raw text to the OpenAI API for structured data extraction
        extracted_data = extract_relevant_data(raw_text)
        print(f"Extracted structured data: {extracted_data}")

        # Check if required fields are present in the extracted data
        if not extracted_data.get('merchant') or not extracted_data.get('date') or not extracted_data.get('amount'):
            print("Error: Missing required fields in the extracted data.")
            return {
                'statusCode': 400,
                'body': json.dumps('Error: Missing required fields in the extracted data.')
            }

        # Step 5: Create receipt metadata and store it in DynamoDB
        receipt_id = object_key.split('/')[-1].split('.')[0]  # Derive receipt ID from S3 object key
        item = {
            'receipt_id': receipt_id,
            'merchant': extracted_data['merchant'],
            'receipt_date': extracted_data['date'],
            'amount': extracted_data['amount'],
            's3_url': f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        }
        print(f"Storing item in DynamoDB: {item}")

        # Store the item in DynamoDB
        table.put_item(Item=item)
        print(f"Receipt metadata stored successfully for {receipt_id}.")

        return {
            'statusCode': 200,
            'body': json.dumps(f'Receipt metadata stored successfully for {receipt_id}.')
        }
    except Exception as e:
        print(f"Error processing receipt: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing receipt: {str(e)}')
        }

def extract_raw_text(textract_response):
    """
    Extract raw text from Textract response. The raw text will be sent to the OpenAI API.
    """
    raw_text = ""
    for block in textract_response['Blocks']:
        if block['BlockType'] == 'LINE':
            raw_text += block['Text'] + "\n"
    return raw_text.strip()  # Remove leading/trailing whitespace

def extract_relevant_data(raw_text):
    """
    Send the extracted text to the OpenAI API for structured data extraction using the chat-based model.

    Args:
        raw_text (str): The extracted text from the receipt.

    Returns:
        dict: Interpreted structured data (e.g., merchant, date, amount).
    """
    messages = [
        {
            "role": "system",
            "content": "You are a data extraction system that extracts relevant information from receipts. Extract key details like merchant name, date, and amount."
        },
        {
            "role": "user",
            "content": f"Extract the merchant name, date, and amount from the following receipt text:\n\n{raw_text}\n\nReturn the information in this JSON format:\n{{\"merchant\": \"\", \"date\": \"\", \"amount\": \"\"}}"
        }
    ]

    try:
        # Use the chat completion endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or "gpt-4"
            messages=messages,
            temperature=0.0
        )

        # Extract and return the response as a dictionary
        extracted_data = response['choices'][0]['message']['content'].strip()
        print(f"Extracted Data from OpenAI: {extracted_data}")  # Print extracted data

        # Convert the extracted JSON string to a dictionary
        structured_data = json.loads(extracted_data)
        return structured_data

    except json.JSONDecodeError:
        print("Error: OpenAI response is not a valid JSON. Check the response format.")
        return {
            "merchant": "",
            "date": "",
            "amount": ""
        }
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return {
            "merchant": "",
            "date": "",
            "amount": ""
        }
