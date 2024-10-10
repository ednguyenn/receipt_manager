import boto3
import json

# Initialize the necessary AWS clients
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Receipts')

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

        # Step 4: Create receipt metadata and store it in DynamoDB
        receipt_id = object_key.split('/')[-1].split('.')[0]  # Derive receipt ID from S3 object key
        item = {
            'receipt_id': receipt_id,
            'raw_text': raw_text,  # Store the raw text extracted from the receipt
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
    Extract raw text from Textract response. The raw text will be stored in DynamoDB.
    """
    raw_text = ""
    for block in textract_response['Blocks']:
        if block['BlockType'] == 'LINE':
            raw_text += block['Text'] + "\n"
    return raw_text.strip()  # Remove leading/trailing whitespace
