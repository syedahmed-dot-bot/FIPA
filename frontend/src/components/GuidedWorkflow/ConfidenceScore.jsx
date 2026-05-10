function ConfidenceScore({ confidence }) {
  const percentage = Math.round(confidence * 100);
  const level = percentage >= 75 ? "high" : percentage >= 50 ? "medium" : "low";

  return (
    <div className={`confidence-score ${level}`}>
      <span>Confidence: {percentage}%</span>
      {level === "low" && (
        <span className="confidence-warning">
          ⚠ Low confidence — verify with senior engineer
        </span>
      )}
    </div>
  );
}

export default ConfidenceScore;