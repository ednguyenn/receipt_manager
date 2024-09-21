// src/components/Authentication/Signup.js

import React, { useState } from 'react';
import { Auth } from 'aws-amplify';
import './Auth.css';

function Signup({ onSignup }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [confirmationCode, setConfirmationCode] = useState('');
  const [step, setStep] = useState(1);

  const [error, setError] = useState('');

  const handleSignup = async (event) => {
    event.preventDefault();

    try {
      await Auth.signUp({
        username: email,
        password,
        attributes: { email },
      });
      console.log('Signup successful');
      setStep(2);
    } catch (err) {
      console.error('Error signing up', err);
      setError(err.message || 'Error signing up');
    }
  };

  const handleConfirmation = async (event) => {
    event.preventDefault();

    try {
      await Auth.confirmSignUp(email, confirmationCode);
      console.log('Confirmation successful');
      onSignup();
    } catch (err) {
      console.error('Error confirming sign up', err);
      setError(err.message || 'Error confirming sign up');
    }
  };

  return (
    <div className="auth-container">
      <h2>Sign Up</h2>
      {error && <div className="auth-error">{error}</div>}
      {step === 1 && (
        <form onSubmit={handleSignup}>
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
            Sign Up
          </button>
        </form>
      )}
      {step === 2 && (
        <form onSubmit={handleConfirmation}>
          <div className="auth-field">
            <label>Confirmation Code:</label>
            <input
              type="text"
              value={confirmationCode}
              onChange={(e) => setConfirmationCode(e.target.value)}
              required
            />
            <small>
              Please check your email for the confirmation code.
            </small>
          </div>
          <button type="submit" className="auth-button">
            Confirm
          </button>
        </form>
      )}
      <div className="auth-footer">
        Already have an account? <a href="/login">Login</a>
      </div>
    </div>
  );
}

export default Signup;
