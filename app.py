from flask import Flask, render_template, request, jsonify
import boto3
import os
from s3_utils import upload_to_s3, get_receipt_image_url
from dynamodb_utils import query_receipts
from llm_search_utils import interpret_query_with_openai


app = Flask(__name__)



# Home page that displays the upload and search interface
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_receipt():
    # Get the uploaded file (image of the receipt)
    file = request.files['file']
    
    # Generate a unique identifier for the receipt (used for the S3 key)
    receipt_id = os.urandom(16).hex()

    # Upload the receipt image to S3
    s3_url = upload_to_s3(receipt_id, file)  # Call the S3 utility function

    # Return a response indicating that the upload was successful
    return jsonify({
        "message": "Receipt uploaded successfully!",
        "s3_url": s3_url
    })

@app.route('/search', methods=['POST'])
def search_receipt():
    # Step 1: Get the search query from the user input (e.g., "find me a Starbucks receipt from 5th of July")
    search_query = request.form['query']

    # Step 2: Use OpenAI API to interpret the query and extract structured data (merchant, date, amount)
    structured_data = interpret_query_with_openai(search_query)
    
    # Extract the interpreted values
    merchant = structured_data.get('merchant', '').strip() or None
    date = structured_data.get('date', '').strip() or None
    amount = structured_data.get('amount', '').strip() or None

    # Step 3: Query DynamoDB for receipts matching the extracted information
    results = query_receipts(merchant=merchant, receipt_date=date, amount=amount)

    # Step 4: Retrieve the S3 URLs for the matching receipts
    for result in results:
        receipt_id = result['receipt_id']
        # Generate and add the S3 image URL to the result dictionary
        result['image_url'] = get_receipt_image_url(receipt_id)

    # Step 5: Render the search results page with the receipt images
    return render_template('results.html', results=results)

# List all receipts
@app.route('/list', methods=['GET'])
def list_receipts():
    # Query DynamoDB to list all receipts
    receipts = query_receipts()
    return render_template('list.html', receipts=receipts)

if __name__ == '__main__':
    app.run(debug=True)
