function ConfidenceScore({ confidence }) {
  const score = Math.round(confidence);
  const level = score >= 7 ? "high" : score >= 5 ? "medium" : "low";

  return (
    <div className={`confidence-score ${level}`}>
      <span>Confidence: {score}/10</span>
      {level === "low" && (
        <span className="confidence-warning">
          ⚠ Low confidence — verify with senior engineer
        </span>
      )}
    </div>
  );
}

export default ConfidenceScore;