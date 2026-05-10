function DomainCard({ domain, title, description, onClick }) {
  return (
    <div className={`domain-card ${domain}`} onClick={onClick}>
      <h2>{title}</h2>
      <p>{description}</p>
      <span className="card-arrow">→</span>
    </div>
  );
}

export default DomainCard;