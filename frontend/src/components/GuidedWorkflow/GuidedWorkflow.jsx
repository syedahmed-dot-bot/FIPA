import { useState } from "react";
import PromptList from "./PromptList.jsx";
import ResponseDisplay from "./ResponseDisplay.jsx";
import ConfidenceScore from "./ConfidenceScore.jsx";
import "./GuidedWorkflow.css";

function GuidedWorkflow({ selectedDomain, setCurrentPage }) {
  const [keyword, setKeyword] = useState("");
  const [keywordSubmitted, setKeywordSubmitted] = useState(false);
  const [prompts, setPrompts] = useState([]);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [response, setResponse] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingPrompts, setLoadingPrompts] = useState(false);

  const handleKeywordSubmit = async () => {
    if (!keyword.trim()) return;
    setLoadingPrompts(true);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/generate-prompts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: selectedDomain,
          keyword: keyword
        })
      });
      const data = await res.json();
      setPrompts(data.prompts);
      setKeywordSubmitted(true);
    } catch (error) {
      setPrompts([]);
    } finally {
      setLoadingPrompts(false);
    }
  };

  const handlePromptSelect = async (prompt) => {
    setSelectedPrompt(prompt);
    setLoading(true);
    setResponse(null);
    setConfidence(null);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: selectedDomain,
          keyword: keyword,
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
        {!keywordSubmitted ? (
          <div className="keyword-input-container">
            <h3>What equipment are you working on?</h3>
            <p>Enter the equipment name to get specific diagnostics</p>
            <div className="keyword-input-row">
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleKeywordSubmit()}
                placeholder={selectedDomain === "drilling" ? "e.g. mud pump, top drive, BOP..." : "e.g. heat exchanger, control valve..."}
                className="keyword-input"
              />
              <button
                className="keyword-submit-btn"
                onClick={handleKeywordSubmit}
                disabled={loadingPrompts}
              >
                {loadingPrompts ? "Loading..." : "Search →"}
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="keyword-tag">
              Equipment: <strong>{keyword}</strong>
              <button
                className="keyword-reset"
                onClick={() => {
                  setKeywordSubmitted(false);
                  setKeyword("");
                  setPrompts([]);
                  setSelectedPrompt(null);
                  setResponse(null);
                  setConfidence(null);
                }}
              >
                ✕ Change
              </button>
            </div>
            <PromptList
              prompts={prompts}
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
          </>
        )}
      </div>
    </div>
  );
}

export default GuidedWorkflow;