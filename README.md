project-root/
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Authentication/
│   │   │   │   ├── Login.js
│   │   │   │   ├── Signup.js
│   │   │   │   └── Auth.css
│   │   │   ├── ReceiptUpload/
│   │   │   │   ├── UploadForm.js
│   │   │   │   └── UploadForm.css
│   │   │   ├── ReceiptSearch/
│   │   │   │   ├── SearchBar.js
│   │   │   │   └── SearchBar.css
│   │   │   └── ReceiptDisplay/
│   │   │       ├── ReceiptList.js
│   │   │       └── ReceiptItem.js
│   │   ├── assets/
│   │   │   └── images/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── styles/
│   │       └── main.css
│   ├── package.json
│   ├── package-lock.json
│   └── .env
├── backend/
│   ├── lambda_functions/
│   │   ├── receipt_processor/
│   │   │   ├── index.js
│   │   │   ├── package.json
│   │   │   └── node_modules/
│   │   └── search_handler/
│   │       ├── index.js
│   │       ├── package.json
│   │       └── node_modules/
│   ├── config/
│   │   └── awsConfig.js
│   ├── package.json
│   ├── package-lock.json
│   └── .env
├── infrastructure/
│   ├── cloudformation/
│   │   ├── s3_bucket.yaml
│   │   ├── dynamodb_table.yaml
│   │   ├── lambda_functions.yaml
│   │   └── cognito_user_pool.yaml
│   └── terraform/
│       └── main.tf
├── database/
│   └── dynamodb/
│       └── setup_scripts/
│           └── create_table.js
├── llm_api/
│   ├── api_calls/
│   │   ├── searchLLM.js
│   │   └── llm_helpers.js
│   ├── config/
│   │   └── llmConfig.js
│   └── package.json
├── scripts/
│   ├── deploy_frontend.sh
│   ├── deploy_backend.sh
│   └── setup_env.sh
├── tests/
│   ├── frontend_tests/
│   │   └── App.test.js
│   └── backend_tests/
│       └── lambda_tests/
│           └── receipt_processor.test.js
├── docs/
│   ├── README.md
│   ├── API_Documentation.md
│   └── architecture_diagram.png
├── .gitignore
└── README.md
