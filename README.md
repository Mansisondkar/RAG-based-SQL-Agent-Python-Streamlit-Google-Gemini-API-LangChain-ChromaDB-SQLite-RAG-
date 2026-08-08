RAG-Based SQL Agent
An AI-powered **Text-to-SQL** web application that converts plain English 
questions into accurate SQL queries using **Retrieval-Augmented Generation (RAG)**.


## Project Structure

```
retail_Sales_Dataset/
├── app.py                    ← Streamlit UI (main entry point)
├── config.py                 ← Paths, API settings, RAG chunks
├── database.py               ← CSV → SQLite loader + query executor
├── rag_engine.py             ← ChromaDB vector store + retrieval
├── llm_engine.py             ← Gemini API (SQL gen + insights)
├── sql_validator.py          ← SQL safety & syntax validation
├── requirements.txt          ← All dependencies
├── retail_sales_dataset.csv  ← Your original dataset (1001 rows)
├── retail_sales.db           ← Auto-created SQLite database
└── chroma_store/             ← Auto-created ChromaDB vector store
```

---

## Step-by-Step Setup & Run Guide

### Step 1 — Install Python (if not installed)

Download Python 3.10+ from https://python.org  
Make sure to check **"Add Python to PATH"** during installation.

---

### Step 2 — Open PowerShell in the project folder

```powershell
cd "C:\Users\Suryakant\Downloads\retail_Sales_Dataset"
```

---

### Step 3 — Create & activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### Step 4 — Install all dependencies

```powershell
pip install -r requirements.txt
```

This installs: Streamlit, ChromaDB, sentence-transformers, OpenAI SDK, Plotly, pandas, sqlparse.

> ⏳ First install downloads the `all-MiniLM-L6-v2` embedding model (~90 MB). Please wait.

---

### Step 5 — Get your Gemini API Key

1. Go to https://ai.google.dev/gemini-api/docs/api-key
2. Sign up / log in → **API Keys** → Create a new key
3. Copy the key (starts with `sk-...`)

---

### Step 6 — Run the App

```powershell
streamlit run app.py
```

The browser will open automatically at **http://localhost:8501**

---

### Step 7 — Using the App

1. **Paste your Gemini API key** in the sidebar (🔑 field)
2. The database and RAG store are **auto-initialized** on startup
3. **Type a question** in the text box (or click a sample question)
4. Click **🚀 Run Query**
5. Watch the pipeline execute step-by-step:
   - RAG retrieval → SQL generation → validation → execution → chart → insights

---

## Sample Questions You Can Ask

| Question | What it does |
|----------|-------------|
| What is the total revenue by product category? | Category-wise aggregation |
| Show monthly sales trend for 2023 | Time series line chart |
| Which gender spends more on average? | Gender comparison |
| Top 10 customers by total spending | Ranking query |
| Revenue breakdown by age group | CASE-based grouping |
| What is the best-selling category for females? | Filtered aggregation |
| How many transactions happened each month? | Monthly count |

---

## Architecture

```
User Question
      ↓
  Streamlit UI (app.py)
      ↓
  RAG Retrieval (rag_engine.py + ChromaDB)
      ↓  [schema + example context]
  LLM Prompt → DeepSeek API (llm_engine.py)
      ↓  [SQL query]
  SQL Validator (sql_validator.py)
      ↓  [safe SELECT only]
  SQLite Execution (database.py)
      ↓  [results DataFrame]
  Auto-Chart (Plotly)  +  Insight Generation (DeepSeek)
      ↓
  Display in Streamlit
```

---

## Environment Variables (Optional)

Instead of entering the API key in UI, create a `.env` file:

```
Gemini_API_KEY=sk-your-key-here
```

---
## Image 
<img width="1340" height="577" alt="Screenshot 2026-08-08 123925" src="https://github.com/user-attachments/assets/67cc5fa3-1238-441b-bfbf-d584ff5ffa9d" />

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `chromadb` import error | Run `pip install chromadb==0.5.3` |
| `sentence_transformers` slow first run | It downloads the model (~90MB), wait once |
| API key error | Check key at platform.deepseek.com |
| Port 8501 busy | Run `streamlit run app.py --server.port 8502` |
