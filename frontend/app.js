// app.js

// Login Handling
document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('https://<your-api-url>/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            alert('Login successful!');
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('upload-section').style.display = 'block';
            document.getElementById('search-section').style.display = 'block';
        } else {
            alert('Login failed.');
        }
    } catch (error) {
        alert('Login failed.');
    }
});

// Receipt Upload Handling
document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const file = document.getElementById('file-input').files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('https://<your-s3-upload-url>', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            alert('Receipt uploaded successfully!');
        } else {
            alert('Upload failed.');
        }
    } catch (error) {
        alert('Upload failed.');
    }
});

// Search Handling
document.getElementById('search-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const query = document.getElementById('search-query').value;

    try {
        const response = await fetch('https://<your-api-url>/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const results = await response.json();
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '<h3>Search Results:</h3>';
        results.forEach(receipt => {
            resultsDiv.innerHTML += `<p>Vendor: ${receipt.vendor_name}, Date: ${receipt.transaction_date}, Total: ${receipt.total_amount}</p>`;
        });
    } catch (error) {
        alert('Search failed.');
    }
});
