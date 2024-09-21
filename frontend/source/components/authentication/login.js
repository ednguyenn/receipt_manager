// src/components/Authentication/Login.js

import React, { useState } from 'react';
import { Auth } from 'aws-amplify';
import './Auth.css';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      await Auth.signIn(email, password);
      console.log('Login successful');
      onLogin();
    } catch (err) {
      console.error('Error logging in', err);
      setError('Incorrect username or password');
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      {error && <div className="auth-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="auth-field">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="auth-field">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="auth-button">
          Login
        </button>
      </form>
      <div className="auth-footer">
        Don't have an account? <a href="/signup">Sign Up</a>
      </div>
    </div>
  );
}

export default Login;
