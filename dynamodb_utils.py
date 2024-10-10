import boto3
from boto3.dynamodb.conditions import Attr

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Define your DynamoDB table
TABLE_NAME = 'Receipts'
table = dynamodb.Table(TABLE_NAME)

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