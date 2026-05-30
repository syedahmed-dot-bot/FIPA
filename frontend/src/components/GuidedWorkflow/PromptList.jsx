import React from "react";
import ReactMarkdown from "react-markdown";

function PromptList({ prompts, onPromptSelect, selectedPrompt }) {
  return (
    <div className="prompt-list">
      <h3>Select your issue:</h3>
      {prompts.map((prompt, index) => (
        <button
          key={index}
          className={`prompt-btn ${selectedPrompt === prompt ? "active" : ""}`}
          onClick={() => onPromptSelect(prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}

export default PromptList;