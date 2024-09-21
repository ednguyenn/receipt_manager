import boto3
import json
import os
import openai  
from boto3.dynamodb.conditions import Key, Attr

# Initialize AWS clients
dynamodb_client = boto3.resource('dynamodb')

# DynamoDB table name (set this in your Lambda environment variables)
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ReceiptsTable')

# OpenAI API key (set this in your Lambda environment variables)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI API key
openai.api_key = OPENAI_API_KEY

# Reference to the DynamoDB table
receipts_table = dynamodb_client.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    Lambda function handler to process search queries.
    """

    # Log the received event for debugging
    print("Received event: " + json.dumps(event, indent=2))

    # Extract the search query and user_id from the event
    try:
        body = json.loads(event.get('body', '{}'))
        search_query = body.get('query', '').strip()
        user_id = body.get('user_id', '').strip()
    except Exception as e:
        print(f"Error parsing event body: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request format.'})
        }

    if not search_query or not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Search query and user_id are required.'})
        }

    print(f"Search query: {search_query}")
    print(f"User ID: {user_id}")

    # Use LLM to interpret the query and generate filters
    try:
        filters = generate_filters(search_query)
        print(f"Generated filters: {filters}")
    except Exception as e:
        print(f"Error generating filters: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error processing search query.'})
        }

    # Add user_id to the filters
    filters['user_id'] = user_id

    # Query DynamoDB using the filters
    try:
        results = query_dynamodb(filters)
        print(f"Query results: {results}")
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error querying database.'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'receipts': results})
    }

def generate_filters(search_query):
    """
    Uses an LLM to generate DynamoDB filters based on the search query.
    """
    # Example prompt to the LLM
    prompt = f"""
Given the following natural language search query, generate a JSON object containing filters to query a DynamoDB table of receipts.

Search Query: "{search_query}"

The DynamoDB table has the following attributes:
- user_id (String)
- vendor_name (String)
- total_amount (Number)
- transaction_date (String, format YYYY-MM-DD)
- items (List of Maps with keys: item_name, quantity, price)
- Any other extracted fields from the receipt.

The output should be a valid JSON object containing the filter attributes and their desired values. For example:
{{
    "vendor_name": "Woolworths",
    "transaction_date": {{
        "between": ["2023-09-01", "2023-09-30"]
    }}
}}

Constraints:
- Dates should be in the format YYYY-MM-DD.
- If the query mentions a date range like "early September", translate it to an appropriate date range.
- Ensure the output is a valid JSON object.

Provide only the JSON object in your response.
"""

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=150,
        temperature=0.2,
        n=1,
        stop=None
    )

    # Extract the filters from the response
    filters_text = response.choices[0].text.strip()
    print(f"LLM Response: {filters_text}")

    # Parse the JSON filters
    try:
        filters = json.loads(filters_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        raise ValueError("LLM did not return valid JSON.")

    return filters

def query_dynamodb(filters):
    """
    Queries the DynamoDB table using the provided filters.
    """
    # Build the key condition expression (assuming user_id is the partition key)
    user_id = filters.pop('user_id')
    key_condition = Key('user_id').eq(user_id)

    # Initialize the filter expression
    filter_expression = None

    # Build filter expressions based on remaining filters
    for attr_name, attr_value in filters.items():
        if isinstance(attr_value, dict):
            if 'between' in attr_value:
                # Handle between conditions (e.g., date ranges)
                start, end = attr_value['between']
                condition = Attr(attr_name).between(start, end)
            elif 'eq' in attr_value:
                # Equality condition
                condition = Attr(attr_name).eq(attr_value['eq'])
            elif 'contains' in attr_value:
                # Contains condition
                condition = Attr(attr_name).contains(attr_value['contains'])
            else:
                continue  # Unsupported condition
        else:
            # Default to equality condition
            condition = Attr(attr_name).eq(attr_value)

        if filter_expression is None:
            filter_expression = condition
        else:
            filter_expression = filter_expression & condition

    # Query the table
    if filter_expression:
        response = receipts_table.query(
            KeyConditionExpression=key_condition,
            FilterExpression=filter_expression
        )
    else:
        response = receipts_table.query(
            KeyConditionExpression=key_condition
        )

    items = response.get('Items', [])
    return items
