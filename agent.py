import os
from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

# Load environment variables from .env file
load_dotenv()

# We use LiteLLM to make it easy to switch AI providers.
# Make sure to set the relevant API key in your .env file!
# For Claude: "anthropic/claude-3-5-sonnet-20241022" (requires ANTHROPIC_API_KEY)
# For OpenAI: "openai/gpt-4o" (requires OPENAI_API_KEY)
# For Gemini: "gemini/gemini-1.5-pro-latest" (requires GEMINI_API_KEY)

# Use Gemini 3 Flash Preview as per new Docs
model = LiteLLMModel(model_id="gemini/gemini-3-flash-preview")

# Initialize the agent with a web search tool.
# The CodeAgent writes and executes python code to solve tasks natively!
agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()], 
    model=model,
    add_base_tools=True # Adds useful basic math and Python functions
)

print("Super Agent Initialized!")
print("Starting reasoning loop...\n")

# Run an example task
# We are using a simple math/coding task because huge web search payloads
# are currently crashing Google's experimental Gemini-3-preview endpoints!
agent.run("Write a python snippet to calculate the first 10 fibonacci numbers.")
