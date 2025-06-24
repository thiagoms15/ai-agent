# 🧠 Agent-AI (Toy Project)

This is a **toy AI agent** built for learning purposes. It integrates with **Google's Gemini API** (`gemini-2.0-flash`) to simulate a coding assistant that can reason through tasks using **tool usage** (function calling). The agent can:

✅ List directory contents  
✅ Read file contents (safely)  
✅ Write to files  
✅ Execute Python files  
✅ Maintain conversation state across turns  
✅ Loop with up to 20 steps of reasoning

---

## 🚨 Disclaimer

> ⚠️ This project is **not production-grade**.  
> It is a **learning exercise** to explore LLM function calling and building agents with memory and execution capabilities.  
> Use it responsibly and **never** connect it to real systems or give it access to sensitive directories.

---

## 🗂️ Project Structure

```bash
agent-ai/
├── calculator/            # Working directory the agent can read/write/execute from
├── functions/             # Tool functions available to the agent
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python.py
├── main.py                # Entry point for the agent
└── tests.py               # Optional test script
```

---

## 🔧 Setup

- Install dependencies: `pip install -r requirements.txt`
- Create a `.env` file with your OpenAI API key: `OPENAI_API_KEY=YOUR_API_KEY`
