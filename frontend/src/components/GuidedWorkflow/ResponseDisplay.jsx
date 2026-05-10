function ResponseDisplay({ response }) {
  return (
    <div className="response-display">
      <h3>Diagnostic Response</h3>
      <div className="response-content">
        {response.split('\n').map((line, index) => (
          line.trim() && <p key={index}>{line}</p>
        ))}
      </div>
    </div>
  );
}

export default ResponseDisplay;