import os
import glob
from dotenv import load_dotenv
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, tool, GradioUI
import chromadb

load_dotenv()

# We are dropping the buggy 'preview' model for a highly stable production model
# the 2.5-flash endpoint is currently globally rate limited (503 outage).
# Reverting to the 3-preview sandbox since it has different traffic channels.
model = LiteLLMModel(model_id="gemini/gemini-3-flash-preview")

# ==========================================
# 0. INITIALIZE LONG TERM MEMORY DB
# ==========================================
print("Loading Memory Database...")
chroma_client = chromadb.PersistentClient(path="./agent_memory")
memory_collection = chroma_client.get_or_create_collection(name="long_term_memory")

# ==========================================
# 1. DEFINE BASE TOOLS
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
def write_to_local_file(filepath: str, content: str) -> str:
    """
    Writes text content to a local file. Use this to create new files or overwrite existing ones.
    
    Args:
        filepath: The exact path to the file you want to write to.
        content: The full text content you want to write into the file.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {filepath}"
    except Exception as e:
        return f"Error writing file {filepath}: {str(e)}"

@tool
def save_memory(memory_key: str, information: str) -> str:
    """
    Saves an important fact, user preference, or context to your long-term memory database.
    
    Args:
        memory_key: A short, unique identifier for this memory (e.g., 'user_name', 'project_goal').
        information: The detailed information or fact you want to remember.
    """
    try:
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
            n_results=2 
        )
        
        documents = results.get("documents", [])
        if not documents or not documents[0]:
            return f"No relevant memories found in database for query: '{search_query}'"
            
        memories = "\n- ".join(documents[0])
        return f"Recalled Memories:\n- {memories}"
    except Exception as e:
        return f"Failed to recall from memory: {str(e)}"

# ==========================================
# 2. INITIALIZE WORKER AGENTS
# ==========================================

print("Hiring Worker Agents...")

# This agent's only job is searching the internet
web_researcher = CodeAgent(
    tools=[DuckDuckGoSearchTool()], 
    model=model
)

# This agent's only job is reading and writing local files
local_engineer = CodeAgent(
    tools=[inspect_local_workspace, read_local_file, write_to_local_file], 
    model=model
)


# ==========================================
# 3. DEFINE DELEGATION TOOLS
# ==========================================

@tool
def delegate_to_researcher(question: str) -> str:
    """
    Passes a complex research question down to your Web Search Employee. 
    Use this when you need live information from the internet. The worker will search and return a clean summary.
    
    Args:
        question: The exact, detailed question you want the researcher to answer using the internet.
    """
    return web_researcher.run(question)

@tool
def delegate_to_engineer(task: str) -> str:
    """
    Passes a file system reading OR writing task down to your Local Engineer worker.
    Use this when you need to read local files, AND ESPECIALLY when you need to CREATE or WRITE to local files. 
    You do NOT have permission to use the open() function yourself. You MUST delegate file creation to this engineer!
    
    Args:
        task: The exact instructions for the engineer (e.g. "Create a file named 'news.txt' with this exact content: ...")
    """
    return local_engineer.run(task)


# ==========================================
# 4. INITIALIZE MANAGER AGENT
# ==========================================

print("Initializing Executive Manager Agent...")

agent = CodeAgent(
    tools=[
        delegate_to_researcher, 
        delegate_to_engineer,
        save_memory,
        recall_memory
    ], 
    model=model,
    add_base_tools=False
)

# ==========================================
# 5. LAUNCH WEB UI
# ==========================================

print("Initializing Gradio Web UI...")
ui = GradioUI(agent)

if __name__ == "__main__":
    ui.launch(share=False)
