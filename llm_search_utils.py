import openai
import os
import json

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_keywords_with_openai(query):
    """
    Use OpenAI to extract keywords from the user's natural language query.

    Args:
        query (str): The user's search query.

    Returns:
        list: A list of keywords extracted from the query.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that extracts keywords from user queries to search receipts."
        },
        {
            "role": "user",
            "content": f"Extract the main keywords from the following query: \"{query}\". "
                       f"Please return the keywords as a JSON array of strings, like this: [\"keyword1\", \"keyword2\", ...]"
        }
    ]

    try:
        # Call OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the appropriate model
            messages=messages,
            temperature=0.0
        )

        # Extract and print the response content for debugging
        raw_response = response['choices'][0]['message']['content'].strip().lower()
        print(f"OpenAI Raw Response: {raw_response}")  # Debugging print

        # Load the response as a JSON array
        keywords = json.loads(raw_response)

        # Ensure that the result is a list of strings
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            keywords = [keyword.lower() for keyword in keywords]
            return keywords
        else:
            print("Error: OpenAI response is not a list of strings.")
            return []

    except json.JSONDecodeError:
        print("Error: OpenAI response is not a valid JSON. Check the response format.")
        print(f"Response Content: {raw_response}")  # Print the problematic response
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return []