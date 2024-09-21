# search_llm.py

import openai
import os
import json

# Initialize OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables.")
openai.api_key = OPENAI_API_KEY

def generate_filters(search_query):
    """
    Uses an LLM to generate DynamoDB filters based on the search query.
    """
    # Define the prompt for the LLM
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

    try:
        # Call the OpenAI Completion API
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
        filters = json.loads(filters_text)

    except Exception as e:
        print(f"Error generating filters: {e}")
        raise ValueError("Failed to generate filters from search query.") from e

    return filters
