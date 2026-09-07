"""Talk-to-Data service wrapping Groq NL-to-SQL and SQLite query execution."""

from typing import Dict, Any, List
from src.talk_to_data.query_runner import TalkToDataEngine
from src.utils.logger import logger

SAMPLE_QUESTIONS = [
    "What is the default rate by income type?",
    "Average loan amount by occupation type?",
    "Top 10 riskiest occupations by default rate?",
    "Show clients with external source score below 0.3",
    "What is the distribution of credit versus annuity amounts across contract types?"
]

class ChatService:
    """Service handling natural-language to SQL exploration of portfolio database."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        logger.info("Initializing ChatService TalkToDataEngine...")
        self.engine = TalkToDataEngine()
        logger.info("ChatService initialized.")

    def get_sample_questions(self) -> List[str]:
        return SAMPLE_QUESTIONS

    def clear_history(self, session_id: str = None) -> None:
        """Clears conversation context from the underlying generator."""
        if hasattr(self, "engine") and hasattr(self.engine, "generator"):
            self.engine.generator.clear_history()
        logger.info(f"Chat history cleared for session: {session_id or 'default'}")

    def process_query(self, question: str) -> Dict[str, Any]:
        """Runs question through NL-to-SQL, executes safely on SQLite, and synthesizes insight."""
        if not question or not question.strip():
            return {
                "success": False,
                "question": question,
                "error": "Query question cannot be empty.",
                "sql": None,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "insight": None,
                "suggested_questions": SAMPLE_QUESTIONS[:3]
            }

        try:
            result = self.engine.answer_question(question.strip())
            
            if not result["success"]:
                return {
                    "success": False,
                    "question": question,
                    "error": result["error"],
                    "sql": result.get("sql"),
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "insight": f"Unable to execute this query: {result['error']}",
                    "suggested_questions": SAMPLE_QUESTIONS[:3]
                }

            df = result["dataframe"]
            columns = df.columns.tolist() if df is not None and not df.empty else []
            rows = df.head(50).to_dict(orient="records") if df is not None and not df.empty else []

            # Dynamic suggested follow-ups
            suggested = [q for q in SAMPLE_QUESTIONS if q.lower() != question.lower()][:3]

            return {
                "success": True,
                "question": question,
                "sql": result["sql"],
                "columns": columns,
                "rows": rows,
                "row_count": result["row_count"],
                "insight": result["insight"],
                "error": None,
                "suggested_questions": suggested
            }

        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "sql": None,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "insight": f"Unable to execute query due to an unexpected system error: {str(e)}",
                "suggested_questions": SAMPLE_QUESTIONS[:3]
            }
