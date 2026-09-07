"""Page 4: Talk-to-Data Conversational NL-to-SQL Agent."""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.talk_to_data.query_runner import TalkToDataEngine
from app.utils.ui import (
    setup_page,
    get_svg_icon,
    render_sidebar_footer,
    FAVICON_PATH
)

st.set_page_config(
    page_title="Talk-to-Data Agent | NeoStats", 
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else None, 
    layout="wide"
)

# Apply global theme (Dark default / Light selectable) and render sidebar
setup_page("Talk-to-Data Agent")

st.title("Talk-to-Data Conversational Agent")
st.markdown("Ask natural-language analytical questions about loan applications, bureau debts, and repayment histories. Backed by **Groq LLM + SQLite**.")

# Initialize session state for conversation
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AI Credit Risk Data Analyst. You can ask me anything about portfolio default rates across cohorts, bureau debt volumes, or applicant demographics.",
            "sql": None,
            "df": None
        }
    ]

# Sidebar with 5 sample queries for evaluators
st.sidebar.markdown(
    """
    <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 6px;">
        Sample Queries
    </div>
    """, 
    unsafe_allow_html=True
)
st.sidebar.caption("Click any query below to run it instantly:")

sample_queries = [
    "What is the default rate by income type?",
    "Average loan amount by occupation type?",
    "Top 10 riskiest occupations by default rate?",
    "Show clients with external source score below 0.3",
    "What is the distribution of credit versus annuity amounts across contract types?"
]

clicked_sample = None
for q in sample_queries:
    if st.sidebar.button(q, use_container_width=True):
        clicked_sample = q

render_sidebar_footer()

# Display previous conversation messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sql"):
            with st.expander("Executed SQL Query", expanded=False):
                st.code(msg["sql"], language="sql")
        if msg.get("df") is not None and not msg["df"].empty:
            with st.expander(f"Query Results Table ({len(msg['df'])} rows)", expanded=False):
                st.dataframe(msg["df"], use_container_width=True)

# User input handling
user_input = st.chat_input("Ask a question about the credit dataset...")
prompt_to_run = clicked_sample or user_input

if prompt_to_run:
    # Append and render user message
    st.session_state.messages.append({"role": "user", "content": prompt_to_run})
    with st.chat_message("user"):
        st.write(prompt_to_run)

    # Generate answer via TalkToDataEngine
    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema, generating SQL, and querying database..."):
            engine = TalkToDataEngine()
            result = engine.answer_question(prompt_to_run)

        if result["success"]:
            # Display narrative insight
            st.markdown(result["insight"])

            # Display executed SQL
            with st.expander("Executed SQL Query", expanded=True):
                st.code(result["sql"], language="sql")

            # Display resulting DataFrame
            df_res = result["dataframe"]
            if df_res is not None and not df_res.empty:
                with st.expander(f"Query Results ({result['row_count']} rows returned)", expanded=True):
                    st.dataframe(df_res, use_container_width=True)

            # Store in session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["insight"],
                "sql": result["sql"],
                "df": df_res
            })
        else:
            error_msg = f"Query Processing Error: {result['error']}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "sql": result.get("sql"),
                "df": None
            })
