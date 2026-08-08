# ─────────────────────────────────────────────
#  app.py  –  SQLMind  |  Streamlit UI
# ─────────────────────────────────────────────
import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from config import CSV_PATH, TABLE_NAME, CHROMA_COLLECTION, GEMINI_API_KEY
from database import load_csv_to_sqlite, execute_query, get_table_info
from rag_engine import build_vector_store, retrieve_context, get_store_stats
from llm_engine import generate_sql, generate_insights
from sql_validator import validate_sql, format_sql
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# ════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SQLMind — Ask Your Data in Plain English",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# ════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
/* ── Hide sidebar completely ── */
[data-testid="stSidebar"]         { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1a2e 100%);
    color: #e2e8f0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}
.hero-banner {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    padding: 2rem 2.5rem;
    border-radius: 1.2rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 40px rgba(99,102,241,0.35);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute; top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.4rem; font-weight: 700; color: #fff;
    margin: 0 0 .4rem; text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.hero-subtitle {
    font-size: 1.05rem; color: rgba(255,255,255,0.85);
    margin: 0; font-weight: 400;
}
.pipeline-wrap {
    display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0 1.6rem;
}
.step-badge {
    display: flex; align-items: center; gap: .4rem;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 999px; padding: .3rem .85rem;
    font-size: .78rem; color: #a5b4fc; font-weight: 500;
}
.step-badge.active {
    background: rgba(99,102,241,0.35); border-color: #6366f1;
    color: #e0e7ff; box-shadow: 0 0 12px rgba(99,102,241,0.4);
}
.metric-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.8), rgba(30,41,59,0.8));
    border: 1px solid rgba(99,102,241,0.2); border-radius: 1rem;
    padding: 1.2rem 1.4rem; text-align: center;
    backdrop-filter: blur(8px); transition: transform .2s, box-shadow .2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(99,102,241,0.25); }
.metric-value {
    font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.metric-label { font-size: .8rem; color: #94a3b8; margin-top: .2rem; font-weight: 500; }
.sql-box {
    background: #0f172a; border: 1px solid rgba(99,102,241,0.35);
    border-left: 4px solid #6366f1; border-radius: .8rem;
    padding: 1.1rem 1.3rem;
    font-family: 'JetBrains Mono','Fira Code',monospace;
    font-size: .85rem; color: #a5b4fc;
    white-space: pre-wrap; word-break: break-all; line-height: 1.7;
}
.insight-box {
    background: linear-gradient(135deg,rgba(6,182,212,0.06),rgba(99,102,241,0.06));
    border: 1px solid rgba(6,182,212,0.25); border-radius: 1rem;
    padding: 1.3rem 1.5rem; color: #e2e8f0; line-height: 1.8;
}
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #e2e8f0;
    border-bottom: 2px solid rgba(99,102,241,0.3);
    padding-bottom: .5rem; margin-bottom: 1rem;
}
.status-success {
    background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4);
    color: #34d399; border-radius: 999px; padding: .2rem .8rem;
    font-size: .78rem; font-weight: 600;
}
.status-error {
    background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4);
    color: #f87171; border-radius: 999px; padding: .2rem .8rem;
    font-size: .78rem; font-weight: 600;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; border: none; border-radius: .7rem;
    padding: .55rem 1.6rem; font-weight: 600; font-size: .95rem;
    transition: all .2s; box-shadow: 0 4px 14px rgba(99,102,241,0.4);
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99,102,241,0.55); }
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #e2e8f0 !important; border-radius: .7rem !important;
}
.stDataFrame { border-radius: .8rem; overflow: hidden; }
div[data-testid="stExpander"] {
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: .8rem !important;
}
</style>
""", unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
def init_session():
    defaults = {
        "db_ready":     False,
        "rag_ready":    False,
        "history":      [],
        "current_step": 0,
        "api_key":      GEMINI_API_KEY,  # pre-load from .env
        "key_confirmed": bool(GEMINI_API_KEY),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════
#  API KEY POPUP
# ════════════════════════════════════════════════════════════════════════════
@st.dialog("🔑 Enter Your API Key")
def api_key_popup():
    st.markdown("""
    <div style='text-align:center;padding:.5rem 0 1rem'>
        <span style='font-size:2.5rem'>🧠</span>
        <h3 style='color:#e2e8f0;margin:.5rem 0 .2rem'>SQLMind needs an API Key</h3>
        <p style='color:#94a3b8;font-size:.9rem;margin:0'>
            Enter your <b>Groq</b> or <b>Gemini</b> free API key to continue
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**⚡ Get a FREE Groq key at** [console.groq.com](https://console.groq.com)")

    key = st.text_input(
        "API Key",
        type="password",
        placeholder="gsk_xxxxxxxxxxxxxxxx  or  AIzaSy-xxxxxxxxxx",
        key="popup_api_key",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save & Continue", use_container_width=True, type="primary"):
            if key.strip():
                st.session_state.api_key      = key.strip()
                st.session_state.key_confirmed = True
                st.rerun()
            else:
                st.error("⚠️ Please enter a valid API key")
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.rerun()

    st.divider()
    st.markdown("""
    <div style='font-size:.8rem;color:#64748b;text-align:center'>
        🔒 Key is stored only for this session &nbsp;|
        &nbsp;ℹ️ Save permanently in your <code>.env</code> file
    </div>
    """, unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:1rem 0 .5rem'>"
            "<span style='font-size:2.5rem'>🧠</span>"
            "<h2 style='color:#e2e8f0;margin:.3rem 0 0;font-size:1.3rem'>SQLMind</h2>"
            "<p style='color:#94a3b8;font-size:.8rem;margin:0'>Ask Your Data in Plain English</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.divider()
        # ── API Key Status (from .env) ───────────────────────────────────────
        if GEMINI_API_KEY:
            st.markdown(
                "<span class='status-success'>🚀 Gemini API Key Loaded</span>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ API key missing!")
            st.markdown("Add to your `.env` file:")
            st.code("GEMINI_API_KEY=AIzaSy_your_key_here", language="bash")
        st.divider()
        # ── System Init ──────────────────────────────────────────────────────
        st.markdown("#### ⚙️ System Setup")
        col1, col2 = st.columns(2)
        with col1:
            db_label = "✅ DB" if st.session_state.db_ready else "🔄 Init DB"
            if st.button(db_label, use_container_width=True, key="btn_db"):
                with st.spinner("Loading CSV…"):
                    ok = load_csv_to_sqlite()
                    st.session_state.db_ready = ok
                st.success("Done!") if ok else st.error("Failed.")
        with col2:
            rag_label = "✅ RAG" if st.session_state.rag_ready else "🔄 Init RAG"
            if st.button(rag_label, use_container_width=True, key="btn_rag"):
                with st.spinner("Building store…"):
                    ok = build_vector_store(force=True)
                    st.session_state.rag_ready = ok
                st.success("Done!") if ok else st.error("Failed.")
        # Auto-init
        if not st.session_state.db_ready:
            st.session_state.db_ready = load_csv_to_sqlite()
        if not st.session_state.rag_ready:
            st.session_state.rag_ready = build_vector_store()
        # ── System Status ────────────────────────────────────────────────────
        st.divider()
        st.markdown("#### 📊 System Status")
        db_info  = get_table_info()
        rag_info = get_store_stats()
        st.markdown(f"**Table:** `{TABLE_NAME}`")
        st.markdown(f"**Rows:** `{db_info.get('row_count', '—'):,}`")
        st.markdown(f"**RAG chunks:** `{rag_info.get('total_chunks', '—')}`")
        st.markdown(f"**Model:** `{rag_info.get('embedding_model', '—')}`")
        
        # ── History ──────────────────────────────────────────────────────────
        if st.session_state.history:
            st.divider()
            st.markdown("#### 🕒 Query History")
            for i, h in enumerate(reversed(st.session_state.history[-5:])):
                with st.expander(f"Q{len(st.session_state.history)-i}: {h['question'][:40]}…"):
                    st.code(h["sql"], language="sql")
# ════════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ════════════════════════════════════════════════════════════════════════════
PIPELINE_STEPS = [
    ("💬", "User Query"),
    ("🔍", "RAG Retrieval"),
    ("🧠", "SQL Generation"),
    ("✅", "Validation"),
    ("🗄️", "Execution"),
    ("📊", "Results"),
    ("💡", "Insights"),
]
def render_pipeline(active: int = -1, slot=None):
    badges = ""
    for i, (icon, label) in enumerate(PIPELINE_STEPS):
        cls = "step-badge active" if i <= active else "step-badge"
        badges += f'<div class="{cls}">{icon} {label}</div>'
    html = f'<div class="pipeline-wrap">{badges}</div>'
    if slot:
        slot.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════════════
#  CHART HELPERS
# ════════════════════════════════════════════════════════════════════════════
CHART_TEMPLATE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
)
GRAD_COLORS = ["#6366f1","#8b5cf6","#06b6d4","#10b981","#f59e0b","#ef4444"]
def auto_chart(df: pd.DataFrame, question: str):
    if df.empty or len(df.columns) < 2:
        return None
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    nrows    = len(df)
    q_lower  = question.lower()
    try:
        if any(w in q_lower for w in ["month","trend","time","year","daily","weekly"]):
            x = cat_cols[0] if cat_cols else df.columns[0]
            y = num_cols[0] if num_cols else df.columns[1]
            fig = px.line(df, x=x, y=y,
                title=f"📈 {y.replace('_',' ').title()} Over Time",
                markers=True, color_discrete_sequence=GRAD_COLORS, **CHART_TEMPLATE)
            fig.update_traces(line_width=3, marker_size=8)
            return fig
        if cat_cols and num_cols and nrows <= 20:
            x, y = cat_cols[0], num_cols[0]
            if nrows <= 6:
                fig = px.pie(df, names=x, values=y,
                    title=f"🥧 {y.replace('_',' ').title()} by {x.replace('_',' ').title()}",
                    color_discrete_sequence=GRAD_COLORS, hole=0.4)
                fig.update_layout(**CHART_TEMPLATE)
            else:
                fig = px.bar(df, x=x, y=y,
                    title=f"📊 {y.replace('_',' ').title()} by {x.replace('_',' ').title()}",
                    color=x, color_discrete_sequence=GRAD_COLORS, text_auto=".2s")
                fig.update_layout(**CHART_TEMPLATE)
                fig.update_traces(textfont_size=11, textangle=0, cliponaxis=False)
            return fig
        if cat_cols and len(num_cols) > 1:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[:3], barmode="group",
                title="📊 Comparison", color_discrete_sequence=GRAD_COLORS)
            fig.update_layout(**CHART_TEMPLATE)
            return fig
        if len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                title="🔵 Correlation", color_discrete_sequence=GRAD_COLORS)
            fig.update_layout(**CHART_TEMPLATE)
            return fig
    except Exception as e:
        logger.warning(f"Chart error: {e}")
    return None
# ════════════════════════════════════════════════════════════════════════════
#  METRICS STRIP
# ════════════════════════════════════════════════════════════════════════════
def render_metrics(df: pd.DataFrame):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        return
    cols = st.columns(min(len(num_cols) + 1, 5))
    with cols[0]:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{len(df):,}</div>'
            f'<div class="metric-label">Rows Returned</div></div>',
            unsafe_allow_html=True,
        )
    for i, col in enumerate(num_cols[:4]):
        val   = df[col].sum() if df[col].dtype in ["float64","int64"] else "—"
        label = col.replace("_"," ").title()
        disp  = f"{val:,.0f}" if isinstance(val,(int,float)) else str(val)
        with cols[i+1]:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{disp}</div>'
                f'<div class="metric-label">Total {label}</div></div>',
                unsafe_allow_html=True,
            )
# ════════════════════════════════════════════════════════════════════════════
#  MAIN QUERY FLOW
# ════════════════════════════════════════════════════════════════════════════
def run_query_flow(question: str):
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        api_key_popup()
        return
    pipeline_slot = st.empty()
    render_pipeline(active=0, slot=pipeline_slot)
    progress_bar  = st.progress(0, "Starting pipeline…")
    status_area   = st.empty()
    try:
        # Step 1 — RAG Retrieval
        status_area.info("🔍 Retrieving context from vector store…")
        progress_bar.progress(14, "RAG retrieval…")
        context = retrieve_context(question)
        render_pipeline(active=1, slot=pipeline_slot)
        with st.expander("📚 RAG Context Retrieved", expanded=False):
            st.markdown(f"```\n{context[:2000]}\n```")
        # Step 2 — SQL Generation
        status_area.info("🧠 Generating SQL with Gemini…")
        progress_bar.progress(28, "SQL generation…")
        render_pipeline(active=2, slot=pipeline_slot)
        sql, gen_error = generate_sql(question, context, api_key=api_key)
        if gen_error:
            st.error(f"❌ SQL generation failed: {gen_error}")
            return
        # Step 3 — Validation
        status_area.info("✅ Validating SQL…")
        progress_bar.progress(42, "SQL validation…")
        render_pipeline(active=3, slot=pipeline_slot)
        is_valid, val_msg = validate_sql(sql)
        formatted_sql     = format_sql(sql)
        st.markdown('<div class="section-header">🧾 Generated SQL Query</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-box">{formatted_sql}</div>', unsafe_allow_html=True)
        if not is_valid:
            st.error(f"❌ SQL Validation Failed: {val_msg}")
            return
        st.markdown(f'<span class="status-success">{val_msg}</span>', unsafe_allow_html=True)
        # Step 4 — Execution
        status_area.info("🗄️ Executing SQL on database…")
        progress_bar.progress(57, "Query execution…")
        render_pipeline(active=4, slot=pipeline_slot)
        rows, columns, exec_error = execute_query(sql)
        if exec_error:
            st.error(f"❌ Query execution failed: {exec_error}")
            return
        if not rows:
            st.warning("⚠️ Query returned no results.")
            progress_bar.progress(100, "Done.")
            return
        # Step 5 — Results
        status_area.info("📊 Rendering results…")
        progress_bar.progress(71, "Rendering results…")
        render_pipeline(active=5, slot=pipeline_slot)
        df = pd.DataFrame(rows, columns=columns)
        st.markdown('<div class="section-header">📊 Query Results</div>', unsafe_allow_html=True)
        render_metrics(df)
        st.markdown("<br>", unsafe_allow_html=True)
        tab_table, tab_chart, tab_raw = st.tabs(["📋 Table","📈 Chart","🔎 Raw JSON"])
        with tab_table:
            st.dataframe(df, use_container_width=True, height=min(400, 40+len(df)*35))
            st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(),
                file_name="results.csv", mime="text/csv")
        with tab_chart:
            fig = auto_chart(df, question)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No chart for this result shape.")
        with tab_raw:
            st.json(rows[:50])
        # Step 6 — Insights
        status_area.info("💡 Generating insights…")
        progress_bar.progress(85, "Generating insights…")
        render_pipeline(active=6, slot=pipeline_slot)
        preview  = df.head(10).to_string(index=False)
        insights, ins_error = generate_insights(question, formatted_sql, preview, api_key=api_key)
        st.markdown('<div class="section-header">💡 Business Insights</div>', unsafe_allow_html=True)
        if ins_error:
            st.warning(f"Could not generate insights: {ins_error}")
        else:
            st.markdown(f'<div class="insight-box">{insights}</div>', unsafe_allow_html=True)
        # Done
        progress_bar.progress(100, "✅ Complete!")
        status_area.success("✅ Pipeline complete!")
        st.session_state.history.append({
            "question": question, "sql": formatted_sql,
            "rows": rows, "columns": columns, "insights": insights,
        })
    except Exception as e:
        st.error(f"🔥 Unexpected error: {e}")
        logger.exception("Unexpected error in query flow")
# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════
def main():
    init_session()
    render_sidebar()

    # ── Auto-show API key popup if no key found ───────────────────────────
    if not st.session_state.get("key_confirmed"):
        api_key_popup()
        return

    # Auto-init DB and RAG silently
    if not st.session_state.db_ready:
        st.session_state.db_ready = load_csv_to_sqlite()
    if not st.session_state.rag_ready:
        st.session_state.rag_ready = build_vector_store()
    # Hero banner
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">🧠 SQLMind</div>
            <div class="hero-subtitle">
                Ask any question about your data in plain English —
                powered by RAG + Gemini AI to auto-generate and execute SQL queries.
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Pipeline (idle)
    render_pipeline(active=-1)
    # Query Input
    prefill  = st.session_state.pop("prefill_question", "")
    st.markdown('<div class="section-header">💬 Ask a Question</div>', unsafe_allow_html=True)
    question = st.text_area(
        "Enter your question",
        value=prefill,
        placeholder="e.g. What is the total revenue by product category?",
        height=100,
        label_visibility="collapsed",
        key="question_input",
    )
    col_btn, col_clr, _ = st.columns([1.5, 1, 5])
    with col_btn:
        run_clicked = st.button("🚀 Run Query", use_container_width=True)
    with col_clr:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    st.divider()
    if run_clicked:
        if not question.strip():
            st.warning("Please enter a question before running.")
        else:
            run_query_flow(question.strip())
    # Dataset Overview
    with st.expander("📂 Dataset Overview", expanded=False):
        try:
            import sqlite3
            from config import DB_PATH
            conn = sqlite3.connect(str(DB_PATH))
            preview_df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} LIMIT 5", conn)
            conn.close()
            st.markdown("**Sample Data (first 5 rows)**")
            st.dataframe(preview_df, use_container_width=True)
            info = get_table_info()
            st.markdown(
                f"**Table:** `{info.get('table')}` &nbsp;|&nbsp; "
                f"**Rows:** `{info.get('row_count','—'):,}` &nbsp;|&nbsp; "
                f"**Columns:** `{len(info.get('columns',[]))}`"
            )
        except Exception as e:
            st.warning(f"Could not load preview: {e}")
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#475569;font-size:.8rem'>"
        "SQLMind · RAG + Gemini AI · Text-to-SQL Analytics"
        "</div>",
        unsafe_allow_html=True,
    )
# ── Entry point ──────────────────────────────────────────────────────────────
main()