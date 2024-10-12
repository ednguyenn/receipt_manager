from flask import Flask, render_template, request, jsonify
import os
from utils import *

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
    #Get the search query from the user input
    search_query = request.form['query']

    #Use OpenAI API to extract keywords from the query
    keywords = extract_keywords_with_openai(search_query)

    if not keywords:
        # If no keywords extracted, return an error message or empty results
        return render_template('results.html', results=[], message="No keywords found in the query.")

    #Query DynamoDB for receipts containing the keywords
    results = query_receipts_by_keywords(keywords)

    #Retrieve the S3 URLs for the matching receipts
    for result in results:
        receipt_id = result['receipt_id']
        # Generate and add the S3 image URL to the result dictionary
        result['image_url'] = get_receipt_image_url(receipt_id)

    #Render the search results page with the receipt images
    return render_template('results.html', results=results)



# List all receipts
@app.route('/list', methods=['GET'])
def list_receipts():
    # Query DynamoDB to list all receipts
    receipts = query_receipts()

    #process receipts to include image URLs
    for receipt in receipts:
        receipt_id = receipt.get('receipt_id')
        if receipt_id:
            receipt['image_url'] = get_receipt_image_url(receipt_id)
        else:
            receipt['image_url'] = None  # Or handle accordingly

    return render_template('list.html', receipts=receipts)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
