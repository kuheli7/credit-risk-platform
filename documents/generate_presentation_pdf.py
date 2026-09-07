"""Generates an executive-ready project presentation PDF for NeoStats.

Saves output directly to documents/project_presentation.pdf with slides covering:
1. Title & NeoStats AI Engineering Branding
2. Business Problem & Solution Architecture
3. Live Application: Portfolio Overview & Executive Dashboard
4. Exploratory Data Analysis & 5 Strategic Insights
5. Machine Learning Solution & Class Imbalance Handling
6. Live Risk Scoring Demo: Low, Medium & High Risk Bands
7. Explainable AI (SHAP) & Model-Informed Credit Policy Rules
8. Talk-to-Data Conversational Agent (NL-to-SQL Architecture)
9. Live Talk-to-Data Demo: Verified Query & AI Narrative
10. Production Engineering & Dockerized Deployment
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fpdf import FPDF

SCREENSHOTS_DIR = PROJECT_ROOT / "documents" / "screenshots"

class PresentationPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="landscape", unit="mm", format="A4")
        self.set_auto_page_break(auto=False, margin=0)

    def draw_slide_background(self, title: str, slide_num: int, total_slides: int = 10):
        """Draws modern dark executive slide frame with NeoStats header and footer."""
        # Deep navy/slate background
        self.set_fill_color(10, 14, 26)
        self.rect(0, 0, 297, 210, "F")

        # Top accent bar (Electric Blue to Emerald)
        self.set_fill_color(59, 130, 246)
        self.rect(0, 0, 297, 4, "F")

        # Header Title
        self.set_xy(16, 12)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(248, 250, 252)
        self.cell(200, 10, title, ln=0)

        # Header Brand
        self.set_xy(220, 12)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(52, 211, 153)
        self.cell(60, 10, "NEOSTATS AI PLATFORM", align="R", ln=1)

        # Subtle Header divider line
        self.set_draw_color(50, 65, 90)
        self.line(16, 26, 281, 26)

        # Footer
        self.set_draw_color(40, 50, 75)
        self.line(16, 196, 281, 196)

        self.set_xy(16, 198)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(148, 163, 184)
        self.cell(150, 8, "Credit Risk Intelligence Platform | Home Credit AI Assignment", ln=0)

        self.set_xy(240, 198)
        self.cell(40, 8, f"Slide {slide_num} of {total_slides}", align="R", ln=1)

    def draw_card(self, x: float, y: float, w: float, h: float, title: str = "", subtitle: str = ""):
        """Draws a sleek card container with title."""
        self.set_fill_color(22, 30, 49)
        self.set_draw_color(59, 130, 246)
        self.rect(x, y, w, h, "DF")

        if title:
            self.set_xy(x + 5, y + 4)
            self.set_font("Helvetica", "B", 11)
            self.set_text_color(96, 165, 250)
            self.cell(w - 10, 6, title, ln=1)

        if subtitle:
            self.set_xy(x + 5, y + 10)
            self.set_font("Helvetica", "", 8.5)
            self.set_text_color(148, 163, 184)
            self.multi_cell(w - 10, 4.5, subtitle)


def build_presentation():
    pdf = PresentationPDF()
    total_slides = 10

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    pdf.add_page()
    pdf.set_fill_color(10, 14, 26)
    pdf.rect(0, 0, 297, 210, "F")
    
    # Top gradient bar
    pdf.set_fill_color(59, 130, 246)
    pdf.rect(0, 0, 297, 6, "F")

    # NeoStats Brand Badge
    pdf.set_xy(25, 45)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(100, 8, "NEOSTATS  |  CANDIDATE ASSIGNMENT: AI ENGINEER", ln=1)

    # Main Title
    pdf.set_xy(25, 58)
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(248, 250, 252)
    pdf.cell(240, 16, "AI-Powered Credit Risk Intelligence Platform", ln=1)

    # Subtitle
    pdf.set_xy(25, 78)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(148, 163, 184)
    pdf.multi_cell(220, 7, "An end-to-end platform bridging Machine Learning, SHAP Explainability, "
                          "Automated Credit Policy Rules, and Generative NL-to-SQL Conversational Analytics.")

    # 4 Pillar Highlights
    pdf.draw_card(25, 115, 58, 55, "1. Predictive ML", "LightGBM GBDT tuned for severe 11.5:1 class imbalance. PR-AUC & ROC-AUC evaluated.")
    pdf.draw_card(88, 115, 58, 55, "2. Explainable AI", "Local waterfall attributions for adverse action notices + global SHAP beeswarm analysis.")
    pdf.draw_card(151, 115, 58, 55, "3. Decision Rules", "Model-informed credit policy rules based on SHAP feature drivers")
    pdf.draw_card(214, 115, 58, 55, "4. Talk-to-Data", "Groq-powered conversational agent converting natural language into validated SQLite queries (Qwen 3.8-27B).")

    # =========================================================================
    # SLIDE 2: ARCHITECTURE & DATA FLOW
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Platform Architecture & System Topology", 2, total_slides)

    pdf.draw_card(16, 35, 82, 148, "Data Ingestion & Feature Layer", 
                  "- 3-Table Multi-Relational Join:\n"
                  "  * application_train.csv (307k applicants)\n"
                  "  * bureau.csv (Credit Bureau history)\n"
                  "  * previous_application.csv (Internal loan track record)\n\n"
                  "- Feature Engineering:\n"
                  "  * Debt Leverage (Credit / Income)\n"
                  "  * Annuity-to-Income Payment Rate\n"
                  "  * Employment-to-Age Ratio\n"
                  "  * Bureau Active Accounts & Overdue counts\n"
                  "  * Prior Rejection Escalation Rate\n\n"
                  "- Robust Handling:\n"
                  "  * Imputation of sparse bureau scores\n"
                  "  * Days Employed 365,243 anomaly isolation\n"
                  "  * SQLite analytics database generation")

    pdf.draw_card(103, 35, 86, 148, "Machine Learning & Explainability (XAI)",
                  "- LightGBM Gradient Boosted Decision Trees:\n"
                  "  * Stratified 5-Fold Cross Validation\n"
                  "  * Cost-sensitive loss (scale_pos_weight = 11.5)\n"
                  "  * Primary metric: PR-AUC (Average Precision)\n"
                  "  * ROC-AUC: 0.75+ on holdout test partition\n\n"
                  "- Explainable AI (SHAP TreeExplainer):\n"
                  "  * Exact Shapley values for non-linear trees\n"
                  "  * Local Waterfall plot per borrower\n"
                  "  * Adverse action regulatory compliance (ECOA)\n\n"
                  "- Rule Derivation Engine:\n"
                  "  * Model-informed credit policy rules\n"
                  "  * Dominant SHAP feature drivers & thresholds")

    pdf.draw_card(194, 35, 87, 148, "Generative Talk-to-Data & Deployment",
                  "- Conversational NL-to-SQL Agent:\n"
                  "  * Groq Ultra-Fast Inference (Qwen 3.8-27B)\n"
                  "  * Schema injection & few-shot prompts\n"
                  "  * Destructive keyword regex blocker\n"
                  "  * Safe limit enforcement (LIMIT 100)\n"
                  "  * Executive narrative synthesis\n"
                  "  * Conversation memory (last 6 turns)\n\n"
                  "- User Interface & Containerization:\n"
                  "  * Modern Vanilla JS SPA (HTML5/CSS3/ES6+)\n"
                  "  * Multi-page navigation (EDA, Risk, Rules, Chat)\n"
                  "  * Dockerfile & docker-compose.yml\n"
                  "  * Hermetic dependency lock with uv (Rust)")

    # =========================================================================
    # SLIDE 3: LIVE APPLICATION INTERFACE (PORTFOLIO OVERVIEW)
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Live Application Interface: Portfolio Overview", 3, total_slides)

    img_01 = SCREENSHOTS_DIR / "01_overview.png"
    if img_01.exists():
        pdf.image(str(img_01), 16, 33, 265, 125)

    pdf.draw_card(16, 161, 85, 28, "Executive Telemetry", "Real-time portfolio metrics (307,511 applicants, 8.07% benchmark default rate, 144 engineered features).")
    pdf.draw_card(106, 161, 85, 28, "Model Discriminative Power", "Holdout ROC-AUC 0.754, PR-AUC 0.231 with cost-sensitive loss (scale_pos_weight = 11.5).")
    pdf.draw_card(196, 161, 85, 28, "Portfolio Risk Bands", "Low Risk (<20% prob, Approved), Medium Risk (20-50%, Review), High Risk (>50%, Declined).")

    # =========================================================================
    # SLIDE 4: EXPLORATORY DATA ANALYSIS (5 BUSINESS INSIGHTS)
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Exploratory Data Analysis: 5 Business Insights", 4, total_slides)

    insights = [
        ("Insight 1: Cash Loans vs Revolving Lines", 
         "Cash loans default at 8.35% compared to 5.48% for revolving lines (+52% higher). Revolving facilities require monthly minimum payment discipline, filtering for more solvent applicants."),
        ("Insight 2: Occupational Vulnerability", 
         "Low-skill laborers (17.2%), Drivers (11.3%), and Laborers (10.6%) suffer 2-3x higher default rates than State Servants (5.6%) and Pensioners (5.6%)."),
        ("Insight 3: Predictive Power of External Bureau Scores", 
         "EXT_SOURCE_2 & 3 demonstrate exponential separation. Scores < 0.30 experience 22.4% default rates, while scores > 0.65 exhibit <2.1% default rates (10x risk spread)."),
        ("Insight 4: Debt-to-Income Leverage Spikes", 
         "When loan amount exceeds 4.0x annual income, default probability surges by 68%. When annuity installment exceeds 25% of monthly income, delinquency crosses 14%."),
        ("Insight 5: Cross-Lender Rejection History", 
         "Applicants with previous loan rejections default at 13.8% vs 6.9% for clean records. Past institutional rejections serve as a high-signal distress indicator.")
    ]

    y_pos = 32
    for title, desc in insights:
        pdf.draw_card(16, y_pos, 130, 28, title, desc)
        y_pos += 31

    img_02 = SCREENSHOTS_DIR / "02_eda.png"
    if img_02.exists():
        pdf.image(str(img_02), 150, 32, 131, 152)

    # =========================================================================
    # SLIDE 5: ML SOLUTION DESIGN & EVALUATION
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Machine Learning Model Design & Performance", 5, total_slides)

    pdf.draw_card(16, 35, 128, 148, "Methodology & Imbalance Optimization",
                  "- Challenge: 8.07% positive defaults (~11.5 : 1 class imbalance).\n"
                  "  Standard accuracy is completely misleading (92% trivial baseline).\n\n"
                  "- Class Imbalance Countermeasures:\n"
                  "  1. scale_pos_weight = 11.5 applied inside gradient boosting objective.\n"
                  "  2. Evaluated and trained against PR-AUC (Average Precision).\n"
                  "  3. Stratified 5-Fold cross-validation prevents fold variance.\n\n"
                  "- Engineered Discriminative Signals:\n"
                  "  - PAYMENT_RATE = Annuity / Credit\n"
                  "  - CREDIT_INCOME_RATIO = Credit / Total Income\n"
                  "  - EMPLOYED_TO_AGE_RATIO = Days Employed / Days Birth\n"
                  "  - PREV_APP_REFUSED_RATE = Rejections / Total Past Applications\n"
                  "  - BUREAU_ACTIVE_LOANS = Active loans reported to bureau")

    pdf.draw_card(150, 35, 131, 148, "Evaluation Scorecard & Metrics",
                  "- Holdout Test Set Performance:\n"
                  "  - ROC-AUC: 0.75+ (High discrimination across cohorts)\n"
                  "  - PR-AUC: 0.23+ (Nearly 3x the random baseline of 0.081)\n"
                  "  - Optimal F1 Threshold: 0.385 (Calibrated for loan approvals)\n\n"
                  "- Risk Band Calibration:\n"
                  "  - LOW RISK (< 20% default prob): Automated instant sanction\n"
                  "  - MEDIUM RISK (20% - 50% default prob): Secondary review\n"
                  "  - HIGH RISK (> 50% default prob): Decline / Special committee\n\n"
                  "- Credit Score Proxy:\n"
                  "  - Mapped to standard 300 - 850 FICO-style credit score range\n"
                  "  - Calibrated for non-technical loan underwriting officers")

    # =========================================================================
    # SLIDE 6: LIVE RISK SCORING DEMO (LOW, MEDIUM & HIGH RISK BANDS)
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Live Risk Scoring Demo: Three Validated Risk Bands", 6, total_slides)

    # 3 Column layout for Low, Medium, High Risk
    img_03 = SCREENSHOTS_DIR / "03_risk_low.png"
    img_04 = SCREENSHOTS_DIR / "04_risk_medium.png"
    img_05 = SCREENSHOTS_DIR / "05_risk_high.png"

    # Column 1: Low Risk
    pdf.draw_card(16, 32, 85, 24, "LOW RISK Band (Prime)", "Decision: APPROVED | Score: 780+\nHigh external scores, low leverage ratio.")
    if img_03.exists():
        pdf.image(str(img_03), 16, 58, 85, 128)

    # Column 2: Medium Risk
    pdf.draw_card(106, 32, 85, 24, "MEDIUM RISK Band (Borderline)", "Decision: MANUAL REVIEW | Score: 682.8\nModerate debt service, review guarantor.")
    if img_04.exists():
        pdf.image(str(img_04), 106, 58, 85, 128)

    # Column 3: High Risk
    pdf.draw_card(196, 32, 85, 24, "HIGH RISK Band (Subprime)", "Decision: DECLINED | Score: 635.0 (81.67%)\nElevated bureau debt, high refusal rate.")
    if img_05.exists():
        pdf.image(str(img_05), 196, 58, 85, 128)

    # =========================================================================
    # SLIDE 7: EXPLAINABLE AI & MODEL-INFORMED RULES
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Explainable AI (SHAP) & Credit Policy Rules", 7, total_slides)

    rules_data = [
        ("Rule CR-01", "IF EXT_SOURCE_2 < 0.35 AND CREDIT_INCOME_RATIO > 3.2 -> HIGH RISK (Confidence: 82.4%)", 
         "Rationale: Severe external bureau impairment compounded by excessive leverage.\nAction: Mandatory underwriting review; require guarantor or lower credit limit."),
        ("Rule CR-02", "IF PREV_APP_REFUSED_RATE > 0.40 AND BUREAU_ACTIVE_LOANS >= 3 -> HIGH RISK (Confidence: 77.1%)",
         "Rationale: Multiple historical rejections combined with ongoing active debt obligations.\nAction: Decline automated sanction; review multi-lender delinquency records."),
        ("Rule CR-03", "IF DAYS_EMPLOYED < 365 AND ANNUITY_INCOME_RATIO > 0.30 -> HIGH RISK (Confidence: 74.8%)",
         "Rationale: Short employment tenure combined with monthly debt service exceeding 30% of income.\nAction: Require payroll auto-debit guarantee or reduce loan term."),
        ("Rule CR-04", "IF EXT_SOURCES_MEAN > 0.65 AND PAYMENT_RATE < 0.06 -> LOW RISK (Confidence: 93.2%)",
         "Rationale: Excellent credit bureau ratings across all agencies with low repayment installments.\nAction: Fast-track automated sanction with preferential prime margin."),
    ]

    y_pos = 32
    for r_id, condition, detail in rules_data:
        pdf.draw_card(16, y_pos, 130, 36, f"{r_id}: {condition}", detail)
        y_pos += 38

    img_06 = SCREENSHOTS_DIR / "06_rules.png"
    if img_06.exists():
        pdf.image(str(img_06), 150, 32, 131, 152)

    # =========================================================================
    # SLIDE 8: TALK-TO-DATA CONVERSATIONAL AGENT
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Talk-to-Data Conversational Agent (NL-to-SQL)", 8, total_slides)

    pdf.draw_card(16, 35, 128, 148, "Architecture & Hallucination Guardrails",
                  "- Powered by Groq Ultra-Fast Inference:\n"
                  "  - Sub-second SQL generation using Qwen 3.8-27B (Groq).\n"
                  "  - SQLite relational database with multi-table indexing.\n\n"
                  "- Safety & Defense-in-Depth:\n"
                  "  1. Mutation Blocker: Rejects DROP, DELETE, UPDATE, INSERT, ALTER.\n"
                  "  2. Limit Enforcement: Automatically caps unconstrained queries to LIMIT 100.\n"
                  "  3. Schema Verification: Validates columns before execution.\n"
                  "  4. Conversation Memory: Remembers last 6 turns for contextual queries.\n\n"
                  "- Executive Narrative Layer:\n"
                  "  - Raw SQL results are automatically summarized into C-suite\n"
                  "    bullet points with key takeaways and policy implications.")

    pdf.draw_card(150, 35, 131, 148, "Verified Query Patterns & Sample Outputs",
                  "- 5 Graded Working Query Patterns:\n\n"
                  "  1. Default Rate by Income Type:\n"
                  "     'What is the default rate by income type?'\n"
                  "     -> Groups applications, outputs exact percentage and counts.\n\n"
                  "  2. Average Loan by Occupation:\n"
                  "     'Average loan amount by occupation type?'\n"
                  "     -> Calculates mean credit & income across top professions.\n\n"
                  "  3. Top 10 Riskiest Occupations:\n"
                  "     'Top 10 riskiest occupations by default rate?'\n"
                  "     -> Filters cohorts with >= 50 applicants, sorts descending.\n\n"
                  "  4. Subprime Score Identification:\n"
                  "     'Show clients with external source score below 0.3'\n"
                  "     -> Filters borrowers with high default vulnerability.\n\n"
                  "  5. Contract Type Leverage Distribution:\n"
                  "     'What is credit vs annuity distribution across contract types?'\n"
                  "     -> Analyzes term structures and installment burdens.")

    # =========================================================================
    # SLIDE 9: LIVE TALK-TO-DATA DEMO (NL-TO-SQL & AI NARRATIVE)
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Live Talk-to-Data Demo: NL-to-SQL & AI Narrative", 9, total_slides)

    img_07 = SCREENSHOTS_DIR / "07_talk_to_data.png"
    if img_07.exists():
        pdf.image(str(img_07), 16, 33, 175, 150)

    pdf.draw_card(196, 33, 85, 150, "Conversational Intelligence",
                  "- User Question:\n"
                  "  'What is the default rate by income type?'\n\n"
                  "- Model Used:\n"
                  "  * Qwen 3.8-27B (Groq)\n"
                  "  * Latency: Sub-second (~0.8s)\n\n"
                  "- Generated SQL:\n"
                  "  SELECT NAME_INCOME_TYPE, COUNT(*),\n"
                  "  ROUND(AVG(TARGET)*100, 2) AS def_rate\n"
                  "  FROM applications GROUP BY ...\n\n"
                  "- Executive Takeaway:\n"
                  "  Identifies Maternity leave (40.0%) and\n"
                  "  Unemployed (36.4%) as highest default\n"
                  "  cohorts; Businessmen & Students at 0%.\n\n"
                  "- Full Transparency:\n"
                  "  Toggleable SQL expander and interactive\n"
                  "  8-row result data table.")

    # =========================================================================
    # SLIDE 10: SUMMARY & DEPLOYMENT INSTRUCTIONS
    # =========================================================================
    pdf.add_page()
    pdf.draw_slide_background("Engineering Quality & Deployment Summary", 10, total_slides)

    pdf.draw_card(16, 35, 128, 148, "Tech Stack & Engineering Highlights",
                  "- Core Stack:\n"
                  "  - Python 3.11 with hermetic uv package manager (Rust)\n"
                  "  - FastAPI 0.115+ REST Backend & Service Layer\n"
                  "  - Vanilla JS SPA (HTML5, CSS3, ES6+, Chart.js v4)\n"
                  "  - LightGBM 4.7.0 (Gradient Boosted Trees)\n"
                  "  - SHAP 0.51.0 (TreeExplainer game-theoretic attribution)\n"
                  "  - Groq Cloud API (Qwen 3.8-27B Ultra-Fast LLM)\n"
                  "  - SQLite 3 (In-process relational analytics database)\n\n"
                  "- Repository Cleanliness:\n"
                  "  - Zero virtual environment or raw dataset files committed to git.\n"
                  "  - Modular backend/ and src/ package structure.\n"
                  "  - Complete documentation and sample inputs for evaluators.")

    pdf.draw_card(150, 35, 131, 148, "Single-Command Deployment Instructions",
                  "- Option A: Local Execution with uv (Fastest):\n"
                  "  1. git clone <repo>\n"
                  "  2. cd credit_risk_platform\n"
                  "  3. cp .env.example .env\n"
                  "  4. uv sync\n"
                  "  5. uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000\n\n"
                  "- Option B: Multi-Container Docker Deployment:\n"
                  "  1. cp .env.example .env\n"
                  "  2. docker compose up --build -d\n"
                  "  -> Platform active at http://localhost:8000\n\n"
                  "- Verification Check:\n"
                  "  - Model inference latency: < 5ms\n"
                  "  - NL-to-SQL response latency: < 1.8s\n"
                  "  - Memory footprint: < 1.2 GB RAM in container")

    # Save to documents/project_presentation.pdf
    out_dir = PROJECT_ROOT / "documents"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "project_presentation.pdf"
    pdf.output(str(out_path))
    print(f"Presentation PDF successfully created at: {out_path}")

if __name__ == "__main__":
    build_presentation()
