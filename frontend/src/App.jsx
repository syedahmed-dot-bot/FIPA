import { useState } from "react";
import HomePage from "./components/HomePage/HomePage.jsx";
import GuidedWorkflow from "./components/GuidedWorkflow/GuidedWorkflow.jsx";
import ChatBot from "./components/ChatBot/ChatBot.jsx";

function App() {
  const [currentPage, setCurrentPage] = useState("homepage");
  const [selectedDomain, setSelectedDomain] = useState(null);

  const renderPage = () => {
    switch (currentPage) {
      case "homepage":
        return <HomePage 
          setCurrentPage={setCurrentPage} 
          setSelectedDomain={setSelectedDomain} 
        />;
      case "guidedWorkflow":
        return <GuidedWorkflow 
          selectedDomain={selectedDomain}
          setCurrentPage={setCurrentPage}
        />;
      case "chatbot":
        return <ChatBot 
          setCurrentPage={setCurrentPage} 
          domain={selectedDomain} 
        />;
      default:
        return <HomePage 
          setCurrentPage={setCurrentPage}
          setSelectedDomain={setSelectedDomain}
        />;
    }
  };

  return (
    <div className="app">
      {renderPage()}
    </div>
  );
}

export default App;