```
receipt-manager/
│
├── frontend/
│   ├── index.html          # Minimal frontend (HTML + JavaScript for interacting with APIs)
│   ├── styles.css          # (Optional) Styling for the frontend (if needed)
│   └── scripts.js          # JavaScript logic to interact with AWS API Gateway
│
├── backend/
│   ├── lambda_functions/
│   │   ├── upload_receipt/
│   │   │   ├── app.py      # Lambda function to upload receipt to S3 and store metadata in DynamoDB
│   │   │   └── requirements.txt  # Python dependencies (boto3, etc.)
│   │   ├── search_receipt/
│   │   │   ├── app.py      # Lambda function to search receipts using Bedrock and DynamoDB
│   │   │   └── requirements.txt  # Python dependencies
│   │   ├── list_receipts/
│   │   │   ├── app.py      # Lambda function to list all receipts stored in DynamoDB
│   │   │   └── requirements.txt  # Python dependencies
│   │
│   ├── infrastructure/
│   │   ├── s3_bucket_setup.py    # Script for S3 bucket creation (if not using CloudFormation)
│   │   ├── dynamodb_setup.py     # Script for setting up the DynamoDB table (if not using CloudFormation)
│   │   ├── api_gateway_setup.py  # Script to set up API Gateway and link it to Lambda functions (optional)
│   │   └── cloudformation.yaml   # (Optional) Infrastructure as Code for S3, DynamoDB, API Gateway, Lambda (CloudFormation Template)
│
├── tests/
│   ├── test_upload_function.py   # Unit tests for the upload_receipt Lambda function
│   ├── test_search_function.py   # Unit tests for the search_receipt Lambda function
│   └── test_list_function.py     # Unit tests for the list_receipts Lambda function
│
└── README.md                     # Instructions for setting up and running the project
```
