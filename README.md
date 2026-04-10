# Super Agent Quickstart 🚀

Welcome to your new autonomous AI agent! This environment harnesses the power of local Python execution to build an AI that doesn't just chat, but can autonomously navigate the web and write its own code to solve complex tasks.

## 🧠 What's under the hood?
1. **`smolagents`**: The orchestrator. It manages the agent's memory, tracks the reasoning loop ("Thoughts" -> "Actions" -> "Observations"), and safely executes the python snippets the agent generates.
2. **`LiteLLM`**: The universal proxy. It translates standard requests to work with Google Gemini, Anthropic Claude, or OpenAI seamlessly under the hood.
3. **`duckduckgo-search`**: The agent's window to the live internet, enabling it to pull real-time data instead of relying on its training cutoff.

## 📂 File Structure
- `agent.py`: The control center. This is where you swap AI models, define new tools, and write the prompt you want the agent to execute.
- `.env`: **Security First!** This file holds your sensitive API keys. It is strictly ignored by version control so you never accidentally leak your keys to GitHub.
- `requirements.txt`: The dependencies needed to recreate this environment on any machine.

## 🛠️ How to Run
Whenever you open a new terminal, make sure to activate your virtual environment before running the agent:

```bash
source .venv/bin/activate
python agent.py
```

> [!NOTE]  
> If you are using an experimental model (like `gemini-3-flash-preview`) and the terminal spits out an **`Internal Server Error (500)`** midway through a reasoning sequence, don't panic! It is not a bug in your code. Preview APIs frequently become unstable during high volumes or long context windows. Simply wait 5 seconds and run `python agent.py` again.

## 🐙 GitHub Integration
A secure `.gitignore` has been provided to protect your `.env` file. To link this folder to your GitHub, run these commands in your terminal:

```bash
git init
git add .
git commit -m "Initial commit: Scaffolded Super Agent"
git branch -M main
```

Then, go to GitHub.com, create a new empty repository, copy its "Remote URL", and link it:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```
