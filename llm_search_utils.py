import openai
import os
import json

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def interpret_query_with_openai(query):
    """
    Use the OpenAI API to interpret a natural language query.

    Args:
        query (str): The user's natural language query.

    Returns:
        dict: Interpreted structured data (e.g., merchant, date, amount).
    """
    # Create a structured prompt to guide the LLM in extracting information from the query
    prompt = f"""
    You are an intelligent assistant. I will provide you with a natural language query about receipts, and you need to extract key information such as the merchant, date of the transaction, and total amount in JSON format.

    Query: "{query}"

    Please extract the information and return it in this JSON format:

    {{
        "merchant": "",
        "date": "",
        "amount": ""
    }}

    Only return valid and correctly formatted data. Do not include any additional information.
    """

    try:
        # Call OpenAI API to process the query
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  
            prompt=prompt,
            max_tokens=150,
            temperature=0.0
        )

        # Extract the response text and convert it to a dictionary
        extracted_data = response['choices'][0]['text'].strip()

        # Convert the extracted JSON text to a dictionary and return it
        structured_data = json.loads(extracted_data)
        return structured_data

    except Exception as e:
        print(f"Error interpreting query with OpenAI: {str(e)}")
        return {
            "merchant": "",
            "date": "",
            "amount": ""
        }
