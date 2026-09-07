"""Natural Language to SQL conversion using Groq Llama-3.3-70B."""

import re
import sqlite3
from typing import Dict, Any, List, Optional
from groq import Groq

from src.utils.config import DB_PATH, GROQ_API_KEY
from src.utils.logger import logger
from src.talk_to_data.prompt_templates import SYSTEM_PROMPT_V2

# Forbidden SQL keywords to prevent destructive or unauthorized operations
FORBIDDEN_SQL_PATTERN = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|ATTACH|DETACH|PRAGMA|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE
)
MAX_SQL_LIMIT = 500
LIMIT_PATTERN = re.compile(r"\bLIMIT\s+(\d+)\b", re.IGNORECASE)

class NLToSQLGenerator:
    """Generates sanitized, executable SQLite queries from plain text."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not set. NL-to-SQL will fail unless configured.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key, timeout=20.0)
            
        self.model = "qwen/qwen3.8-27b"
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_turns = 6

    def _sanitize_sql(self, raw_sql: str) -> str:
        """Cleans and validates the generated SQL string."""
        # Strip code fences and surrounding whitespaces
        cleaned = re.sub(r"```(?:sql)?", "", raw_sql, flags=re.IGNORECASE).strip()
        cleaned = cleaned.rstrip(";").strip()

        if ";" in cleaned:
            raise ValueError("Invalid SQL: Multiple statements are not allowed.")

        # Check for forbidden mutations
        if FORBIDDEN_SQL_PATTERN.search(cleaned):
            match = FORBIDDEN_SQL_PATTERN.search(cleaned).group(0)
            raise ValueError(f"Security Alert: Destructive SQL keyword '{match.upper()}' detected.")

        # Ensure query is a read operation
        upper_query = cleaned.upper().strip()
        if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
            raise ValueError("Invalid SQL: Query must begin with SELECT or WITH.")

        limit_matches = LIMIT_PATTERN.findall(cleaned)
        if len(limit_matches) > 1:
            raise ValueError("Invalid SQL: Only one LIMIT clause is allowed.")

        if limit_matches and int(limit_matches[0]) > MAX_SQL_LIMIT:
            raise ValueError(f"Invalid SQL: LIMIT cannot exceed {MAX_SQL_LIMIT}.")

        # Validate table and column names without executing the query.
        if DB_PATH.exists():
            try:
                with sqlite3.connect(DB_PATH) as connection:
                    connection.execute(f"EXPLAIN QUERY PLAN {cleaned}")
            except sqlite3.Error as exc:
                raise ValueError(f"Invalid SQL schema or syntax: {exc}") from exc

        # Append default safety limit if missing.
        if not limit_matches:
            cleaned += " LIMIT 100"

        return cleaned + ";"

    def generate_sql(self, question: str) -> Dict[str, Any]:
        """Translates user natural language query into a validated SQL string."""
        if not self.client:
            return {
                "success": False,
                "error": "Groq API key not configured. Please supply GROQ_API_KEY in .env.",
                "sql": None
            }

        try:
            # Build messages payload with conversation history
            messages = [{"role": "system", "content": SYSTEM_PROMPT_V2}]
            for turn in self.conversation_history[-self.max_history_turns * 2:]:
                messages.append(turn)

            messages.append({"role": "user", "content": question})

            logger.info(f"Dispatching query to Groq ({self.model}): '{question}'")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
                max_tokens=600,
            )

            raw_sql = response.choices[0].message.content.strip()
            validated_sql = self._sanitize_sql(raw_sql)

            # Record into conversation history
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": validated_sql})

            logger.info(f"Generated SQL: {validated_sql}")
            return {
                "success": True,
                "sql": validated_sql,
                "raw_response": raw_sql,
                "error": None
            }

        except Exception as e:
            logger.error(f"Failed to generate SQL: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql": None
            }

    def clear_history(self):
        """Clears conversation context memory."""
        self.conversation_history = []
        logger.info("NL-to-SQL conversation history cleared.")

# Convenience function
def generate_sql(question: str) -> str:
    """Convenience helper to generate SQL directly."""
    generator = NLToSQLGenerator()
    res = generator.generate_sql(question)
    if res["success"]:
        return res["sql"]
    raise RuntimeError(res["error"])
