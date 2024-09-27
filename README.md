```
receipt-manager/
├── app.py                    # Main Flask application
├── requirements.txt           # Flask and necessary dependencies
├── templates/                 # Jinja2 HTML templates
│   └── index.html             # Main page for upload/search receipts
├── static/                    # Static files (CSS/JS) for the frontend
│   └── main.js                # JavaScript logic to handle API calls (if needed)
├── s3_utils.py                # Utility functions for handling S3 operations
├── dynamodb_utils.py          # Utility functions for handling DynamoDB operations
├── bedrock_utils.py           # Utility functions for Amazon Bedrock calls
├── tests/                     # Unit tests
└── README.md                  # Project documentation

```
