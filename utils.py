import boto3
import os
import openai
import json
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_DEFAULT_REGION')
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize S3 client using credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region
)
# The name of your S3 bucket
BUCKET_NAME = 'my-receipt-manager-bucket'

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Define your DynamoDB table
TABLE_NAME = 'Receipts'
table = dynamodb.Table(TABLE_NAME)


def upload_to_s3(receipt_id, file):
    """
    Upload the receipt image to S3.

    Args:
        receipt_id (str): Unique identifier for the receipt.
        file (File): The file object to be uploaded.
    
    Returns:
        str: The S3 URL of the uploaded file.
    """
    s3_key = f"receipts/{receipt_id}.jpg"
    
    try:
        # Upload the file to the S3 bucket
        s3.upload_fileobj(file, BUCKET_NAME, s3_key)
        
        # Generate the S3 URL
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        raise

def get_receipt_image_url(receipt_id):
    """
    Get the S3 URL for a given receipt ID.

    Args:
        receipt_id (str): The unique identifier for the receipt.
    
    Returns:
        str: The S3 URL of the receipt image.
    """
    # Construct the S3 key for the receipt image
    s3_key = f"receipts/{receipt_id}.jpg"

    # Generate a presigned URL for accessing the image
    s3_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600  # URL expires in 1 hour
    )
    return s3_url



def extract_keywords_with_openai(query):
    """
    Use OpenAI to extract keywords from the user's natural language query.

    Args:
        query (str): The user's search query.

    Returns:
        list: A list of keywords extracted from the query.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that extracts keywords from user queries to search receipts."
        },
        {
            "role": "user",
            "content": f"Extract the main keywords from the following query: \"{query}\". "
                       f"Please return the keywords as a JSON array of strings, like this: [\"keyword1\", \"keyword2\", ...]"
        }
    ]

    try:
        # Call OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the appropriate model
            messages=messages,
            temperature=0.0
        )

        # Extract and print the response content for debugging
        raw_response = response['choices'][0]['message']['content'].strip().lower()
        print(f"OpenAI Raw Response: {raw_response}")  # Debugging print

        # Load the response as a JSON array
        keywords = json.loads(raw_response)

        # Ensure that the result is a list of strings
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            keywords = [keyword.lower() for keyword in keywords]
            return keywords
        else:
            print("Error: OpenAI response is not a list of strings.")
            return []

    except json.JSONDecodeError:
        print("Error: OpenAI response is not a valid JSON. Check the response format.")
        print(f"Response Content: {raw_response}")  # Print the problematic response
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return []
    

def query_receipts_by_keywords(keywords):
    # Build the filter expression
    filter_expression = None
    for keyword in keywords:
        condition = Attr('raw_text').contains(keyword)
        filter_expression = condition if filter_expression is None else filter_expression & condition

    if filter_expression is None:
        return []

    response = table.scan(FilterExpression=filter_expression)
    return response.get('Items', [])

def query_receipts():
    """
    Query DynamoDB to retrieve all receipts.

    Returns:
        list: A list of all receipts.
    """
    receipts = []
    last_evaluated_key = None

    while True:
        if last_evaluated_key:
            response = table.scan(ExclusiveStartKey=last_evaluated_key)
        else:
            response = table.scan()

        items = response.get('Items', [])
        receipts.extend(items)

        # Check if there are more items to retrieve
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

    return receipts