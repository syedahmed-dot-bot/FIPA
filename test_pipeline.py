from backend.agent.workflow_agent import run_workflow_agent
from backend.agent.query import run_query_pipeline
from backend.agent.chat_agent import run_chat_agent

def test_backend():
    print("\n--- FIPA Backend Test ---")

    # Step 1 - Domain selection
    print("\nSelect domain:")
    print("1. drilling")
    print("2. refinery")
    domain_input = input("Enter number: ").strip()
    domain = "drilling" if domain_input == "1" else "refinery"
    print(f"Domain selected: {domain}")

    # Step 2 - Keyword selection
    if domain == "drilling":
        keywords = ["top drive system", "mud pump", "blowout preventer", "drill bit", "rotary table"]
    else:
        keywords = ["heat exchanger", "distillation column", "centrifugal pump", "pressure vessel", "control valve"]

    print("\nSelect equipment keyword:")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")
    kw_input = int(input("Enter number: ").strip())
    keyword = keywords[kw_input - 1]
    print(f"Keyword selected: {keyword}")

    # Step 3 - Generate prompts
    print(f"\nGenerating prompts for {keyword}...")
    prompts = run_workflow_agent(domain, keyword)

    print("\nSelect your issue:")
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt}")
    print("0. Go directly to free chat")

    prompt_input = input("\nEnter number: ").strip()

    # Step 4 - Query pipeline or free chat
    if prompt_input != "0":
        selected_prompt = prompts[int(prompt_input) - 1]
        print(f"\nSelected: {selected_prompt}")
        print("Running query pipeline...")

        result = run_query_pipeline(domain, keyword, selected_prompt)

        print("\n--- RESPONSE ---")
        print(result["response"])
        print(f"\nConfidence: {result['confidence']}")
        print(f"Procurement needed: {result['procurement_needed']}")

        print("\nWas this resolved? (y/n):")
        resolved = input().strip().lower() == "y"

        if resolved:
            print("\nIssue resolved. Session complete.")
            return

        print("\nIssue not resolved. Falling back to free chat...")

    # Step 5 - Free chat
    print("\n--- FREE CHAT MODE ---")
    conversation_history = []

    while True:
        message = input("\nYou: ").strip()
        if message.lower() in ["exit", "quit", "q"]:
            print("Session complete.")
            break

        result = run_chat_agent(message, domain, conversation_history)

        print(f"\nFIPA: {result['response']}")
        print(f"Confidence: {result['confidence']}")

        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": result["response"]})

        print("\nWas this resolved? (y/n/exit):")
        resolved_input = input().strip().lower()
        if resolved_input in ["y", "exit"]:
            print("Session complete.")
            break

if __name__ == "__main__":
    test_backend()