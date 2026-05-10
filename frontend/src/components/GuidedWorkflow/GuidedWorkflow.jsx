import { useState } from "react";
import PromptList from "./PromptList.jsx";
import ResponseDisplay from "./ResponseDisplay.jsx";
import ConfidenceScore from "./ConfidenceScore.jsx";
import "./GuidedWorkflow.css";

function GuidedWorkflow({ selectedDomain, setCurrentPage }) {
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [response, setResponse] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePromptSelect = async (prompt) => {
    setSelectedPrompt(prompt);
    setLoading(true);
    setResponse(null);
    setConfidence(null);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: selectedDomain,
          prompt: prompt
        })
      });
      const data = await res.json();
      setResponse(data.response);
      setConfidence(data.confidence);
    } catch (error) {
      setResponse("Error retrieving response. Please try again.");
      setConfidence(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="guided-workflow">
      <div className="workflow-header">
        <button className="back-btn" onClick={() => setCurrentPage("homepage")}>
          ← Back
        </button>
        <h2>{selectedDomain === "drilling" ? "Drilling & Extraction" : "Refinery Operations"}</h2>
        <button className="chatbot-btn" onClick={() => setCurrentPage("chatbot")}>
          Switch to Free Chat
        </button>
      </div>
      <div className="workflow-body">
        <PromptList
          domain={selectedDomain}
          onPromptSelect={handlePromptSelect}
          selectedPrompt={selectedPrompt}
        />
        {loading && <div className="loading">Retrieving answer...</div>}
        {response && (
          <>
            <ConfidenceScore confidence={confidence} />
            <ResponseDisplay response={response} />
          </>
        )}
      </div>
    </div>
  );
}

export default GuidedWorkflow;