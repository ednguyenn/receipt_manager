import boto3

# Initialize the Bedrock client
bedrock = boto3.client('bedrock')

def interpret_query_with_bedrock(query):
    """
    Interpret the user's natural language query using Amazon Bedrock.

    Args:
        query (str): The user's search query.
    
    Returns:
        dict: Interpreted structured data (e.g., merchant, date).
    """
    try:
        response = bedrock.generate(
            Text=query,
            ModelId="bedrock-model-id"
        )
        
        # Extract and return the interpreted data from the Bedrock response
        interpreted_data = response.get('interpreted_data', {})
        return interpreted_data
    except Exception as e:
        print(f"Error interpreting query with Bedrock: {str(e)}")
        raise
