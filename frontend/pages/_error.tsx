import React from 'react';
import { NextPageContext } from 'next';

interface ErrorProps {
  statusCode: number | null;
}

function Error({ statusCode }: ErrorProps) {
  return (
    <div className="error-container" style={{ 
      padding: '2rem',
      maxWidth: '800px',
      margin: '0 auto',
      fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    }}>
      <h1 style={{ color: '#d32f2f' }}>
        {statusCode ? `Error ${statusCode}` : 'An error occurred'}
      </h1>
      <p>
        {statusCode
          ? `A server-side error occurred. Our team has been notified.`
          : 'An error occurred on the client. Please try again later.'}
      </p>
      <button 
        onClick={() => window.location.href = '/'}
        style={{
          backgroundColor: '#1976d2',
          color: 'white',
          padding: '0.5rem 1rem',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '1rem',
          marginTop: '1rem'
        }}
      >
        Return to Home Page
      </button>
    </div>
  );
}

Error.getInitialProps = ({ res, err }: NextPageContext): ErrorProps => {
  const statusCode = res ? res.statusCode : err ? err.statusCode ?? 500 : 404;
  return { statusCode };
};

export default Error;
