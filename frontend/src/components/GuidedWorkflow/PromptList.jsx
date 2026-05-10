const DRILLING_PROMPTS = [
  "Top Drive System is throwing an error code",
  "Mud Pump pressure loss detected",
  "Blowout Preventer not responding",
  "Drill Bit excessive wear reported",
  "Rotary Table abnormal vibration"
];

const REFINERY_PROMPTS = [
  "Heat Exchanger temperature deviation detected",
  "Distillation Column pressure drop abnormal",
  "Centrifugal Pump cavitation reported",
  "Pressure Vessel safety valve triggered",
  "Control Valve not responding to commands"
];

function PromptList({ domain, onPromptSelect, selectedPrompt }) {
  const prompts = domain === "drilling" ? DRILLING_PROMPTS : REFINERY_PROMPTS;

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