"""Query execution against SQLite and natural language insight synthesis."""

import sqlite3
from typing import Dict, Any, Optional
import pandas as pd
from groq import Groq

from src.utils.config import DB_PATH, GROQ_API_KEY
from src.utils.helpers import initialize_sqlite_db
from src.utils.logger import logger
from src.talk_to_data.nl_to_sql import NLToSQLGenerator
from src.talk_to_data.prompt_templates import INSIGHT_SUMMARY_PROMPT

class TalkToDataEngine:
    """Full-stack Talk-to-Data engine: NL -> SQL -> Execution -> Business Narrative."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        self.generator = NLToSQLGenerator()
        if GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY, timeout=20.0)
        else:
            self.groq_client = None

    def ensure_database_ready(self):
        """Validates that the SQLite DB is populated; initializes if missing."""
        if not self.db_path.exists():
            logger.info("Database not found. Triggering automated SQLite setup...")
            initialize_sqlite_db()

    def execute_sql(self, sql_query: str) -> pd.DataFrame:
        """Executes a validated SELECT query and returns a Pandas DataFrame."""
        self.ensure_database_ready()
        
        conn = sqlite3.connect(self.db_path)
        try:
            logger.info(f"Executing SQL on SQLite: {sql_query}")
            df = pd.read_sql_query(sql_query, conn)
            return df
        finally:
            conn.close()

    def generate_narrative_insight(self, question: str, sql_query: str, df: pd.DataFrame) -> str:
        """Invokes LLM to distill raw tabular results into concise business insights."""
        if not self.groq_client:
            return "Groq API key not configured for narrative generation."

        if df.empty:
            return "No matching records found in the database for the given criteria."

        # Truncate table preview to prevent token overflow
        sample_records = df.head(15).to_markdown(index=False)

        prompt = f"""
User Question: "{question}"
Executed SQL:
{sql_query}

Query Result Preview ({len(df)} total rows returned):
{sample_records}
"""
        try:
            response = self.groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {"role": "system", "content": INSIGHT_SUMMARY_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate narrative insight: {str(e)}")
            return f"Query returned {len(df)} rows. Detailed narrative generation unavailable ({str(e)})."

    def answer_question(self, question: str) -> Dict[str, Any]:
        """End-to-end question answering pipeline for talk-to-data."""
        # 1. Generate SQL
        sql_res = self.generator.generate_sql(question)
        if not sql_res["success"]:
            return {
                "success": False,
                "sql": None,
                "dataframe": None,
                "insight": None,
                "error": sql_res["error"]
            }

        sql_query = sql_res["sql"]

        # 2. Execute SQL
        try:
            df = self.execute_sql(sql_query)
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            return {
                "success": False,
                "sql": sql_query,
                "dataframe": None,
                "insight": None,
                "error": f"Database execution error: {str(e)}"
            }

        # 3. Synthesize Narrative Insight
        insight = self.generate_narrative_insight(question, sql_query, df)

        return {
            "success": True,
            "sql": sql_query,
            "dataframe": df,
            "insight": insight,
            "row_count": len(df),
            "error": None
        }

# Global singleton
_engine = None

def query_credit_data(question: str) -> Dict[str, Any]:
    """Helper function to run NL query through the Talk-to-Data engine."""
    global _engine
    if _engine is None:
        _engine = TalkToDataEngine()
    return _engine.answer_question(question)
