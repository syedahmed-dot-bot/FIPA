import DomainCard from "./DomainCard.jsx";
import "./HomePage.css";

function HomePage({ setCurrentPage, setSelectedDomain }) {
  const handleDomainSelect = (domain) => {
    setSelectedDomain(domain);
    setCurrentPage("guidedWorkflow");
  };

  return (
    <div className="homepage">
      <div className="homepage-header">
        <h1>FIPA</h1>
        <p>Field Intelligence & Procurement Assistant</p>
      </div>
      <div className="domain-cards-container">
        <DomainCard
          domain="drilling"
          title="Drilling & Extraction"
          description="Equipment diagnostics and procurement for drilling operations"
          onClick={() => handleDomainSelect("drilling")}
        />
        <DomainCard
          domain="refinery"
          title="Refinery Operations"
          description="Equipment diagnostics and procurement for refinery operations"
          onClick={() => handleDomainSelect("refinery")}
        />
      </div>
      <button
        className="chatbot-direct-btn"
        onClick={() => setCurrentPage("chatbot")}
      >
        Go directly to Free Chat
      </button>
    </div>
  );
}

export default HomePage;