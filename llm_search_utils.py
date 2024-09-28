import openai
import os
import json

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


def interpret_query_with_openai(query):
    """
    Use the OpenAI API to interpret a natural language query using the chat model.

    Args:
        query (str): The user's natural language query.

    Returns:
        dict: Interpreted structured data (e.g., merchant, date, amount).
    """
    # Create a structured message to guide the LLM in extracting information from the query
    messages = [
        {
            "role": "system",
            "content": "You are a data extraction system that extracts relevant information from a natural language query about receipts."
        },
        {
            "role": "user",
            "content": f"Extract the merchant, date, and amount from this query: '{query}'. Return the result in this JSON format:\n{{\"merchant\": \"\", \"date\": \"\", \"amount\": \"\"}}"
        }
    ]

    try:
        # Call OpenAI's v1/chat/completions endpoint with the chat model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or "gpt-4" for chat-based models
            messages=messages,
            temperature=0.0
        )

        # Extract the response content and convert it to a dictionary
        extracted_data = response['choices'][0]['message']['content'].strip()
        structured_data = json.loads(extracted_data)

        return structured_data

    except Exception as e:
        print(f"Error interpreting query with OpenAI: {str(e)}")
        return {
            "merchant": "",
            "date": "",
            "amount": ""
        }