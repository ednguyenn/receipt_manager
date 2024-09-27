import boto3

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Define your DynamoDB table
TABLE_NAME = 'Receipts'
table = dynamodb.Table(TABLE_NAME)

def store_receipt_metadata(receipt_id, merchant, receipt_date, amount, s3_url):
    """
    Store receipt metadata in DynamoDB.

    Args:
        receipt_id (str): Unique identifier for the receipt.
        merchant (str): The name of the merchant.
        receipt_date (str): The date of the receipt.
        amount (float): The amount spent.
        s3_url (str): The S3 URL of the uploaded receipt.
    
    Returns:
        None
    """
    try:
        table.put_item(
            Item={
                'receipt_id': receipt_id,
                'merchant': merchant,
                'receipt_date': receipt_date,
                'amount': str(amount),
                's3_url': s3_url
            }
        )
    except Exception as e:
        print(f"Error storing receipt metadata: {str(e)}")
        raise

def query_receipts(merchant=None, receipt_date=None):
    """
    Query receipts from DynamoDB based on merchant and date.

    Args:
        merchant (str, optional): Merchant name to filter by.
        receipt_date (str, optional): Receipt date to filter by.
    
    Returns:
        list: List of receipt metadata matching the query.
    """
    try:
        if merchant and receipt_date:
            # Query DynamoDB for matching merchant and receipt date
            response = table.query(
                KeyConditionExpression="merchant = :merchant AND begins_with(receipt_date, :date)",
                ExpressionAttributeValues={
                    ':merchant': merchant,
                    ':date': receipt_date
                }
            )
            return response.get('Items', [])
        else:
            # Scan DynamoDB if no filters are applied
            response = table.scan()
            return response.get('Items', [])
    except Exception as e:
        print(f"Error querying receipts: {str(e)}")
        raise
