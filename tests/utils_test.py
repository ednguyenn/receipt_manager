import pytest
from unittest.mock import patch, MagicMock, mock_open
import utils


# Fixture to set environment variables before tests
@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'fake_access_key')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'fake_secret_key')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-west-2')
    monkeypatch.setenv('OPENAI_API_KEY', 'fake_openai_key')
    # Reload the utils module to pick up the environment variables
    with patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'fake_access_key',
        'AWS_SECRET_ACCESS_KEY': 'fake_secret_key',
        'AWS_DEFAULT_REGION': 'us-west-2',
        'OPENAI_API_KEY': 'fake_openai_key'
    }):
        yield

# Test for upload_to_s3
@patch('utils.s3.upload_fileobj')
def test_upload_to_s3(mock_upload_fileobj):
    receipt_id = '12345'
    file = MagicMock()

    # Call the function
    s3_url = utils.upload_to_s3(receipt_id, file)

    # Assertions
    mock_upload_fileobj.assert_called_once_with(file, utils.BUCKET_NAME, f"receipts/{receipt_id}.jpg")
    assert s3_url == f"https://{utils.BUCKET_NAME}.s3.amazonaws.com/receipts/{receipt_id}.jpg"

# Test for upload_to_s3 with exception
@patch('utils.s3.upload_fileobj', side_effect=Exception('Upload failed'))
def test_upload_to_s3_exception(mock_upload_fileobj, capsys):
    receipt_id = '12345'
    file = MagicMock()

    with pytest.raises(Exception) as exc_info:
        utils.upload_to_s3(receipt_id, file)
    
    mock_upload_fileobj.assert_called_once_with(file, utils.BUCKET_NAME, f"receipts/{receipt_id}.jpg")
    assert str(exc_info.value) == 'Upload failed'
    
    captured = capsys.readouterr()
    assert "Error uploading to S3: Upload failed" in captured.out

# Test for get_receipt_image_url
@patch('utils.s3.generate_presigned_url')
def test_get_receipt_image_url(mock_generate_presigned_url):
    receipt_id = '12345'
    expected_url = 'https://fake_presigned_url.com'

    mock_generate_presigned_url.return_value = expected_url

    # Call the function
    s3_url = utils.get_receipt_image_url(receipt_id)

    # Assertions
    mock_generate_presigned_url.assert_called_once_with(
        'get_object',
        Params={'Bucket': utils.BUCKET_NAME, 'Key': f"receipts/{receipt_id}.jpg"},
        ExpiresIn=3600
    )
    assert s3_url == expected_url

# Test for extract_keywords_with_openai
@patch('utils.openai.ChatCompletion.create')
def test_extract_keywords_with_openai(mock_chat_completion, capsys):
    query = "Find all receipts from Starbucks in March"

    # Mock OpenAI response
    mock_response = {
        'choices': [
            {
                'message': {
                    'content': '["starbucks", "march"]'
                }
            }
        ]
    }
    mock_chat_completion.return_value = mock_response

    # Call the function
    keywords = utils.extract_keywords_with_openai(query)

    # Assertions
    mock_chat_completion.assert_called_once()
    expected_keywords = ["starbucks", "march"]
    assert keywords == expected_keywords

    captured = capsys.readouterr()
    assert "OpenAI Raw Response: [\"starbucks\", \"march\"]" in captured.out

# Test for extract_keywords_with_openai with invalid JSON
@patch('utils.openai.ChatCompletion.create')
def test_extract_keywords_with_openai_invalid_json(mock_chat_completion, capsys):
    query = "Find all receipts from Starbucks in March"

    # Mock OpenAI response with invalid JSON
    mock_response = {
        'choices': [
            {
                'message': {
                    'content': 'starbucks, march'
                }
            }
        ]
    }
    mock_chat_completion.return_value = mock_response

    # Call the function
    keywords = utils.extract_keywords_with_openai(query)

    # Assertions
    mock_chat_completion.assert_called_once()
    assert keywords == []

    captured = capsys.readouterr()
    assert "Error: OpenAI response is not a valid JSON. Check the response format." in captured.out
    assert "Response Content: starbucks, march" in captured.out

# Test for extract_keywords_with_openai with API exception
@patch('utils.openai.ChatCompletion.create', side_effect=Exception('API error'))
def test_extract_keywords_with_openai_exception(mock_chat_completion, capsys):
    query = "Find all receipts from Starbucks in March"

    # Call the function
    keywords = utils.extract_keywords_with_openai(query)

    # Assertions
    mock_chat_completion.assert_called_once()
    assert keywords == []

    captured = capsys.readouterr()
    assert "Error calling OpenAI API: API error" in captured.out

# Test for query_receipts_by_keywords
@patch('utils.table.scan')
def test_query_receipts_by_keywords(mock_scan):
    keywords = ['starbucks', 'march']
    expected_items = [
        {'receipt_id': '1', 'raw_text': 'Starbucks purchase in March'},
        {'receipt_id': '2', 'raw_text': 'March Starbucks order'}
    ]
    mock_scan.return_value = {'Items': expected_items}

    # Call the function
    items = utils.query_receipts_by_keywords(keywords)

    # Assertions
    assert mock_scan.call_count == 1

    # Access keyword arguments
    filter_expression = mock_scan.call_args.kwargs.get('FilterExpression')
    assert filter_expression is not None, "FilterExpression was not passed to table.scan"

# Test for query_receipts_by_keywords with no keywords
def test_query_receipts_by_keywords_no_keywords():
    keywords = []

    # Call the function
    items = utils.query_receipts_by_keywords(keywords)

    # Assertions
    assert items == []

# Test for query_receipts with multiple scans
@patch('utils.table.scan')
def test_query_receipts(mock_scan):
    # Mock responses for pagination
    first_response = {
        'Items': [{'receipt_id': '1'}, {'receipt_id': '2'}],
        'LastEvaluatedKey': {'receipt_id': '2'}
    }
    second_response = {
        'Items': [{'receipt_id': '3'}],
        # No LastEvaluatedKey indicating the end
    }
    mock_scan.side_effect = [first_response, second_response]

    # Call the function
    receipts = utils.query_receipts()

    # Assertions
    assert mock_scan.call_count == 2
    assert receipts == [
        {'receipt_id': '1'},
        {'receipt_id': '2'},
        {'receipt_id': '3'}
    ]

# Test for query_receipts with single scan
@patch('utils.table.scan')
def test_query_receipts_single_scan(mock_scan):
    response = {
        'Items': [{'receipt_id': '1'}, {'receipt_id': '2'}]
        # No LastEvaluatedKey indicating the end
    }
    mock_scan.return_value = response

    # Call the function
    receipts = utils.query_receipts()

    # Assertions
    assert mock_scan.call_count == 1
    assert receipts == [{'receipt_id': '1'}, {'receipt_id': '2'}]

# Test for query_receipts with no items
@patch('utils.table.scan')
def test_query_receipts_no_items(mock_scan):
    response = {
        'Items': []
    }
    mock_scan.return_value = response

    # Call the function
    receipts = utils.query_receipts()

    # Assertions
    assert mock_scan.call_count == 1
    assert receipts == []

