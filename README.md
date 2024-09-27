```
receipt-manager/
│
├── app.py                         # Main Flask app entry point
├── requirements.txt                # Python dependencies (Flask, boto3, etc.)
├── .ebextensions/                  # Elastic Beanstalk configuration folder
│   └── flask.config                # Configuration file for Elastic Beanstalk (optional)
├── templates/                      # Jinja2 HTML templates for the frontend
│   ├── index.html                  # Main page (upload and search)
│   ├── results.html                # Results page for displaying search results
│   └── list.html                   # Page to list all receipts                    # JavaScript (optional for frontend interactions)
├── s3_utils.py                     # Utility file to handle S3 interactions (uploading images)
├── dynamodb_utils.py               # Utility file to handle DynamoDB interactions (store/query receipts)
├── bedrock_utils.py                # Utility file to handle Bedrock interactions (LLM search interpretation)
├── lambda_receipt_processor.py      # Lambda function for extracting text using Textract
├── tests/                          # Unit tests for different components
│   ├── test_s3_utils.py            # Unit test for S3 utilities
│   ├── test_dynamodb_utils.py      # Unit test for DynamoDB utilities
│   ├── test_bedrock_utils.py       # Unit test for Bedrock utilities
│   └── test_lambda.py              # Unit test for Lambda function
├── Dockerfile                      # Dockerfile for containerized deployment (optional)
├── README.md                       # Project documentation and instructions
└── .gitignore                      # Files and directories to ignore in version control


```
