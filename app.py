from flask import Flask, render_template, request, jsonify
import boto3
import os
from s3_utils import upload_to_s3
from dynamodb_utils import store_receipt_metadata, query_receipts
from bedrock_utils import interpret_query_with_bedrock


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

# Search receipt route using Bedrock
@app.route('/search', methods=['POST'])
def search_receipt():
    search_query = request.form['query']
    
    # Call Amazon Bedrock to interpret the query
    interpreted_data = interpret_query_with_bedrock(search_query)
    
    # Extract merchant and date
    merchant = interpreted_data.get('merchant')
    receipt_date = interpreted_data.get('date')
    
    # Query DynamoDB for the receipt
    results = query_receipts(merchant, receipt_date)
    
    return render_template('results.html', results=results)

# List all receipts
@app.route('/list', methods=['GET'])
def list_receipts():
    # Query DynamoDB to list all receipts
    receipts = query_receipts()
    return render_template('list.html', receipts=receipts)

if __name__ == '__main__':
    app.run(debug=True)
