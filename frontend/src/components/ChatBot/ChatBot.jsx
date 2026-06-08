import { useState } from "react";
import "./ChatBot.css";
import ReactMarkdown from 'react-markdown';

function ChatBot({ setCurrentPage, domain }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          { 
            message: input,
            domain: domain,
            conversation_history: []
          }
        )
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Error retrieving response. Please try again."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot">
      <div className="chatbot-header">
        <button className="back-btn" onClick={() => setCurrentPage("homepage")}>
          ← Back
        </button>
        <h2>Free Chat</h2>
      </div>
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}
        {loading && <div className="message assistant"><p>Thinking...</p></div>}
      </div>
      <div className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Describe your issue..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ChatBot;