Receipt Manager is a flask web application built to showcase AWS expertise using a containerized deployment approach. It enables users to upload, store, and search for receipts using AWS services and natural language queries.

Functionality

Upload Receipts: Upload or take a photo of a receipt, which is stored in Amazon S3.
Data Extraction: Automatically extracts merchant, date, and amount details using AWS Textract.
Search & Retrieval: Retrieve receipts using natural language queries like "Starbucks receipts in September" with the help of OpenAI’s LLM.
Receipt Viewing: Displays original receipt images based on search results.
Tech Stack
Frontend & Backend: Flask app containerized with Docker and deployed on EC2 using Amazon ECR.
Storage: Amazon S3 for storing original receipt images.
Database: Amazon DynamoDB for storing receipt metadata.
Data Extraction: AWS Textract for extracting text and data from images.
Authentication: Amazon Cognito.
LLM Integration: OpenAI API for natural language query interpretation.

Deployment
Dockerize the Flask app and push the image to Amazon ECR.
Deploy the Docker container on Fargate.
Use Amazon Cognito for user authentication.
Configure the Flask app to interact with AWS services like S3, DynamoDB, and Textract.
```
.
.
├── app.py
├── bashscripts
│   ├── create_dynamodb_table.sh
│   ├── create_ECS_cluster.sh
│   ├── create_s3_bucket.sh
│   ├── push_to_ECR.sh
│   └── setup_lambda_function.sh
├── compose.yaml
├── Dockerfile
├── dynamodb_utils.py
├── lambda_function.py
├── lambda_function.zip
├── lambda_package
│   └── lambda_function.py
├── llm_search_utils.py
├── note.txt
├── README.Docker.md
├── README.md
├── requirements.txt
├── s3_utils.py
├── templates
│   ├── index.html
│   ├── list.html
│   └── results.html
└── tests

```
