import os
import glob
from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, tool, GradioUI

# Import our new Vector Database!
import chromadb

# Load environment variables
load_dotenv()

# Universal model routing. Ensure your selected provider API key is in .env
model = LiteLLMModel(model_id="gemini/gemini-3-flash-preview")

# ==========================================
# 0. INITIALIZE LONG TERM MEMORY DB
# ==========================================
print("Loading Memory Database...")
# This creates a folder called 'agent_memory' in your project to store data persistently
chroma_client = chromadb.PersistentClient(path="./agent_memory")
# A collection is basically a table in the database where our memories will live
memory_collection = chroma_client.get_or_create_collection(name="long_term_memory")


# ==========================================
# 1. DEFINE CUSTOM TOOLS
# ==========================================

@tool
def inspect_local_workspace(directory: str = ".") -> str:
    """
    Inspects the local file system to find files and folders.
    This gives the agent the ability to understand its environment!
    
    Args:
        directory: The path to the directory you want to inspect. Defaults to "." (current directory).
    """
    try:
        files = glob.glob(f"{directory}/*")
        if not files:
            return f"Directory '{directory}' is empty or does not exist."
        return f"Contents of {os.path.abspath(directory)}:\n" + "\n".join(files)
    except Exception as e:
        return f"Fatal error reading directory: {str(e)}"

@tool
def read_local_file(filepath: str) -> str:
    """
    Reads the full contents of a local file. Use this after inspecting the workspace to read specific code or data.
    
    Args:
        filepath: The exact path to the file you want to read.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"--- FILE: {filepath} ---\n{content}\n--- END OF FILE ---"
    except Exception as e:
        return f"Error reading file {filepath}: {str(e)}"

@tool
def save_memory(memory_key: str, information: str) -> str:
    """
    Saves an important fact, user preference, or context to your long-term memory database.
    
    Args:
        memory_key: A short, unique identifier for this memory (e.g., 'user_name', 'project_goal').
        information: The detailed information or fact you want to remember.
    """
    try:
        # ChromaDB requires a unique ID and a document
        memory_collection.upsert(
            documents=[information],
            ids=[memory_key]
        )
        return f"Successfully saved to memory under database key: {memory_key}"
    except Exception as e:
        return f"Failed to save to memory: {str(e)}"

@tool
def recall_memory(search_query: str) -> str:
    """
    Searches your long-term memory database for saved facts, preferences, or context.
    Use this whenever the user references something from the past or expects you to remember them.
    
    Args:
        search_query: A phrase describing what you are trying to remember (e.g., 'What is the user's name?').
    """
    try:
        results = memory_collection.query(
            query_texts=[search_query],
            n_results=2 # Fetch top 2 most mathematically relevant memories
        )
        
        # Extract the documents from the result payload
        documents = results.get("documents", [])
        if not documents or not documents[0]:
            return f"No relevant memories found in database for query: '{search_query}'"
            
        memories = "\n- ".join(documents[0])
        return f"Recalled Memories:\n- {memories}"
    except Exception as e:
        return f"Failed to recall from memory: {str(e)}"


# ==========================================
# 2. INITIALIZE AGENT
# ==========================================

# We load our new tools into the agent's brain!
agent = CodeAgent(
    tools=[
        DuckDuckGoSearchTool(), 
        inspect_local_workspace, 
        read_local_file,
        save_memory,
        recall_memory
    ], 
    model=model,
    add_base_tools=True
)

# ==========================================
# 3. LAUNCH WEB UI
# ==========================================

print("Initializing Gradio Web UI...")
ui = GradioUI(agent)

if __name__ == "__main__":
    ui.launch(share=False)
