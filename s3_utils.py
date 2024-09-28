import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_DEFAULT_REGION')

# Initialize S3 client using credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region
)



# The name of your S3 bucket
BUCKET_NAME = 'my-receipt-manager-bucket'

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


