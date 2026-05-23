import ReactMarkdown from 'react-markdown';

function ResponseDisplay({ response }) {
  return (
    <div className="response-display">
      <h3>Diagnostic Response</h3>
      <div className="response-content">
        <ReactMarkdown>{response}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ResponseDisplay;
