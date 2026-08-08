#  RAG-Based SQL Agent

An AI-powered **Text-to-SQL** web application that converts plain English 
questions into accurate SQL queries using **Retrieval-Augmented Generation (RAG)**.

##  Features

 **Natural Language to SQL** — Ask questions in plain English
 **RAG Pipeline** — ChromaDB retrieves relevant schema context
 **Google Gemini API** — Generates accurate, context-aware SQL queries
 **SQL Validation** — Validates query before execution
 **SQLite Execution** — Runs query on the database
 **Result Visualization** — Tables, charts & metrics
 **AI Insights** — Business insights generated from results
 **Interactive Dashboard** — Full pipeline visible step-by-step

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core language |
| Streamlit | Web UI |
| Google Gemini API | LLM for SQL generation |
| LangChain | LLM orchestration |
| ChromaDB | Vector store for RAG |
| SQLite | Database |
| Sentence Transformers | Text embeddings |
| Plotly | Data visualization |

##  Pipeline

User Query → RAG Retrieval → SQL Generation → 
Validation → Execution → Results → AI Insights

##  Setup

1. Clone the repository
   git clone https://github.com/yourusername/rag-sql-agent.git
   cd rag-sql-agent

2. Create virtual environment
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies
   pip install -r requirements.txt

4. Add your API key to .env file
   GEMINI_API_KEY=your_google_gemini_api_key

5. Run the app
   streamlit run app.py

##  Get Free Gemini API Key
Visit: https://aistudio.google.com/apikey

## Project Structure

rag-sql-agent/
│
├── app.py              # Main Streamlit UI
├── config.py           # Configuration & settings
├── database.py         # SQLite database setup
├── rag_engine.py       # ChromaDB vector store
├── llm_engine.py       # Gemini API integration
├── sql_validator.py    # SQL validation logic
├── requirements.txt    # Dependencies
├── .env                # API keys (not committed)
└── retail_sales_dataset.csv  # Sample dataset
