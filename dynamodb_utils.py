import boto3

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Define your DynamoDB table
TABLE_NAME = 'Receipts'
table = dynamodb.Table(TABLE_NAME)

def query_receipts(merchant=None, receipt_date=None, amount=None):
    """
    Query receipts from DynamoDB based on merchant, date, and/or amount.

    Args:
        merchant (str, optional): Merchant name to filter by.
        receipt_date (str, optional): Receipt date to filter by.
        amount (str, optional): Receipt amount to filter by.

    Returns:
        list: List of receipt metadata matching the query.
    """
    try:
        # Prepare the filter expression based on available parameters
        filter_expression = []
        expression_attribute_values = {}

        if merchant:
            filter_expression.append("contains(merchant, :merchant)")
            expression_attribute_values[':merchant'] = merchant
        
        if receipt_date:
            filter_expression.append("contains(receipt_date, :receipt_date)")
            expression_attribute_values[':receipt_date'] = receipt_date

        if amount:
            filter_expression.append("contains(amount, :amount)")
            expression_attribute_values[':amount'] = amount

        # Combine the filter expression if multiple filters are provided
        filter_expression_str = " AND ".join(filter_expression) if filter_expression else None

        # Perform a scan operation on the DynamoDB table with the filter expression
        if filter_expression_str:
            response = table.scan(
                FilterExpression=filter_expression_str,
                ExpressionAttributeValues=expression_attribute_values
            )
        else:
            # If no filters provided, return all receipts
            response = table.scan()

        return response.get('Items', [])

    except Exception as e:
        print(f"Error querying receipts: {str(e)}")
        return []