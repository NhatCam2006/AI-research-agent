# 🤖 AI Research Agent with LangGraph & Groq

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-v0.2-green)
![Groq](https://img.shields.io/badge/Groq-Llama3-orange)

An autonomous AI Agent designed to conduct deep research on any given topic. Built with **LangGraph**, powered by **Groq (Llama 3.3)** for ultra-fast reasoning, and **Tavily API** for real-time web searching.

## 🚀 Features

- **Iterative Research:** The agent doesn't just search once. It critiques its own findings and searches again if information is missing.
- **Self-Reflection:** Includes a "Critique Node" that evaluates the quality of the gathered data before writing.
- **Fast Inference:** Utilizes Groq's LPU to run the Llama 3.3-70b model at lightning speeds.
- **State Management:** Uses LangGraph `StateGraph` to manage the workflow context effectively.

## 🛠 Tech Stack

- **Framework:** LangChain & LangGraph
- **LLM Engine:** Groq (Model: `llama-3.3-70b-versatile`)
- **Search Tool:** Tavily Search API
- **Environment:** Python

## ⚙️ Work Flow

1.  **Search Node:** Queries the web for information about the user's topic.
2.  **Critique Node:** The AI analyzes the search results.
    - If the info is **"NOTFULL"**: It generates a better search query and loops back to the Search Node.
    - If the info is **"FULL"**: It proceeds to the Write Node.
3.  **Write Node:** Synthesizes all gathered information into a concise, professional report.

## 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/YOUR_USERNAME/ai-research-agent.git](https://github.com/YOUR_USERNAME/ai-research-agent.git)
    cd ai-research-agent
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    TAVILY_API_KEY=your_tavily_api_key_here
    ```

## 🏃‍♂️ Usage

Run the agent with the following command:

```bash
python main.py
```
