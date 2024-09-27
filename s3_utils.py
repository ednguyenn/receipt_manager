import boto3

# Initialize the S3 client
s3 = boto3.client('s3')

# The name of your S3 bucket
BUCKET_NAME = 'your-receipt-manager-bucket'

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
