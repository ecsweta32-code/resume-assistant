# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from src.pdf_parser import extract_text
from src.graph import app as langgraph_app
from src.report_builder import build_pdf_report

# Load environment variables
load_dotenv()

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise AI Resume Screener",
    page_icon="📋",
    layout="wide",
)

# ── Session state bootstrap ──────────────────────────────────────────────────
# screening_history : dict[str, dict]
#   key   → candidate display name
#   value → {final_output, timestamp, filename}
if "screening_history" not in st.session_state:
    st.session_state.screening_history = {}

if "current_view" not in st.session_state:
    st.session_state.current_view = None


# ── Helper: score badge colour ───────────────────────────────────────────────
def _score_dot(score: int) -> str:
    if score >= 75:
        return "🟢"
    elif score >= 50:
        return "🟡"
    return "🔴"


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Session History (Step 2)
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🗂️ Screening History")
    st.caption("Switch between candidates screened this session.")

    if st.session_state.screening_history:
        for name, record in st.session_state.screening_history.items():
            score = record["final_output"].get("score_report", {}).get("score", 0)
            dot   = _score_dot(score)
            label = f"{dot} {name}  ·  {score}/100\n{record['timestamp']}"

            is_active = st.session_state.current_view == name
            btn_type  = "primary" if is_active else "secondary"

            if st.button(label, key=f"hist_{name}", use_container_width=True, type=btn_type):
                st.session_state.current_view = name
                st.rerun()

        st.divider()
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.screening_history = {}
            st.session_state.current_view = None
            st.rerun()
    else:
        st.info("No candidates screened yet in this session.")


# ════════════════════════════════════════════════════════════════════════════
# MAIN INTERFACE
# ════════════════════════════════════════════════════════════════════════════
st.title("📋 AI Resume Screening Assistant")
st.subheader("Powered by LangGraph & Gemini 2.5")

col_input, col_report = st.columns([1, 1], gap="large")


# ── LEFT: Input panel ────────────────────────────────────────────────────────
with col_input:
    st.header("📥 New Assessment")

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    default_jd = (
        "Python Developer\n\nSkills Required:\n"
        "- Python\n- FastAPI\n- SQL\n- Docker\n- LangGraph\n- AWS"
    )
    job_description = st.text_area("Job Description", value=default_jd, height=250)

    submit_button = st.button(
        "🚀 Analyze Resume", type="primary", use_container_width=True
    )


# ── RIGHT: Report panel ──────────────────────────────────────────────────────
with col_report:
    st.header("📊 Screening Report")

    # ── Handle a new analysis submission ────────────────────────────────────
    if submit_button:
        if uploaded_file is not None and job_description.strip():
            from datetime import datetime

            candidate_name = (
                uploaded_file.name.replace(".pdf", "")
                .replace("_", " ")
                .title()
            )

            with st.spinner(f"🧠 Processing pipeline for {candidate_name}…"):
                try:
                    temp_dir = "temp"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, uploaded_file.name)

                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    resume_text = extract_text(temp_path)

                    initial_state = {
                        "resume_text":        resume_text,
                        "job_description":    job_description,
                        "resume_chunks":      [],
                        "score_report":       {},
                        "summary":            "",
                        "interview_questions": [],
                        "final_report":       "",
                    }

                    final_output = langgraph_app.invoke(initial_state)
                    os.remove(temp_path)

                    # ── Save to history (Step 2) ─────────────────────────
                    st.session_state.screening_history[candidate_name] = {
                        "final_output": final_output,
                        "timestamp":    datetime.now().strftime("%d %b %Y, %H:%M"),
                        "filename":     uploaded_file.name,
                    }
                    st.session_state.current_view = candidate_name
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
        else:
            st.warning("⚠️ Please provide both a resume PDF and a job description.")

    # ── Render the active candidate report ──────────────────────────────────
    active = st.session_state.current_view

    if active and active in st.session_state.screening_history:
        record       = st.session_state.screening_history[active]
        data         = record["final_output"]
        score_report = data.get("score_report", {})
        score        = score_report.get("score", 0)

        st.success(f"✅ Viewing Report for: **{active}**  ·  *{record['timestamp']}*")

        # ── FEATURE 1: Visual Score Gauges & Metrics ─────────────────────
        m1, m2, m3 = st.columns([1, 2, 1])

        with m1:
            st.metric("Match Score", f"{score} / 100")

        with m2:
            st.progress(score / 100)

        with m3:
            dot = _score_dot(score)
            verdict = (
                f"{dot} Strong Match" if score >= 75
                else f"{dot} Partial Match" if score >= 50
                else f"{dot} Weak Match"
            )
            st.markdown(f"**{verdict}**")

        # Quick skill pills
        matched = score_report.get("matched_skills", [])
        missing = score_report.get("missing_skills", [])

        if matched or missing:
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("**✅ Matched Skills**")
                st.markdown(
                    " ".join(f"`{s}`" for s in matched) if matched
                    else "_None identified_"
                )
            with p2:
                st.markdown("**❌ Missing Skills**")
                st.markdown(
                    " ".join(f"`{s}`" for s in missing) if missing
                    else "_None identified_"
                )

        st.divider()

        # Full markdown report
        st.markdown(data.get("final_report", ""))

        st.divider()

        # ── FEATURE 3: Export to PDF (Step 3) ────────────────────────────
        try:
            pdf_bytes = build_pdf_report(active, data)
            safe_name = active.lower().replace(" ", "_")

            st.download_button(
                label="📥 Download PDF Evaluation Report",
                data=pdf_bytes,
                file_name=f"{safe_name}_screening_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as pdf_err:
            st.warning(f"PDF generation failed: {pdf_err}")

    else:
        st.info(
            "Upload a resume on the left and click **Analyze Resume**, "
            "or select a candidate from the sidebar history."
        )
