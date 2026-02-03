# -------------------------------------------------------
# Travel Guide App (Streamlit + OpenAI)
# - Collects trip preferences
# - Uses dropdowns for interests & guardrails
# - Generates day-by-day travel itinerary
# - Exports itinerary to a clean PDF
# -------------------------------------------------------

import os
from datetime import datetime
from textwrap import dedent

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# PDF
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# -------------------------
# ENV SETUP
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# STREAMLIT CONFIG
# -------------------------
st.set_page_config(
    page_title="Travel Guide",
    page_icon="🌍",
    layout="centered",
)

# -------------------------
# DROPDOWN OPTIONS
# -------------------------
INTEREST_OPTIONS = [
    "Museums",
    "Food & Cuisine",
    "Historic Sites",
    "Nightlife",
    "Nature & Outdoors",
    "Shopping",
    "Adventure Activities",
    "Beaches",
    "Art & Culture",
    "Local Experiences",
]

GUARDRAIL_OPTIONS = [
    "No walking tours",
    "Kid-friendly activities only",
    "Wheelchair accessible places only",
    "Low physical activity",
    "Indoor activities preferred",
    "Avoid nightlife",
    "Budget-friendly options only",
    "Public transport only",
]

# -------------------------
# SESSION STATE (TYPED)
# -------------------------
def init_state():
    st.session_state.setdefault("destination", "")
    st.session_state.setdefault("days", 1)
    st.session_state.setdefault("interests", [])
    st.session_state.setdefault("guardrails", [])
    st.session_state.setdefault("plan_md", "")

def reset_all():
    st.session_state["destination"] = ""
    st.session_state["days"] = 1
    st.session_state["interests"] = []
    st.session_state["guardrails"] = []
    st.session_state["plan_md"] = ""
    st.session_state.pop("last_model_used", None)

init_state()

# -------------------------
# UI HEADER
# -------------------------
st.title("🌍 Travel Guide")
st.caption("AI-powered personalized travel planning")

with st.expander("What this app does"):
    st.markdown(
        """
        - Builds a **day-by-day itinerary**
        - Uses **interests & guardrails**
        - Produces a **downloadable PDF**
        """
    )

# -------------------------
# PROMPTS
# -------------------------
SYSTEM_PROMPT = dedent("""
You are an expert TRAVEL PLANNER.

Rules:
- Produce a realistic, efficient itinerary.
- Divide the trip strictly by day (Day 1, Day 2, etc.).
- Balance pace; avoid overpacked days.
- Respect ALL guardrails strictly (zero violations).
- Prefer famous attractions plus local hidden gems.
- Avoid activities that violate accessibility, safety, or constraints.

Output format in Markdown using:
## Trip Overview
## Day-by-Day Itinerary
### Day 1
- Morning
- Afternoon
- Evening
## Travel Tips
""").strip()

def build_user_prompt(destination, days, interests, guardrails):
    interests_text = ", ".join(interests) if interests else "General sightseeing"
    guardrails_text = ", ".join(guardrails) if guardrails else "None"

    return dedent(f"""
    TRAVEL DETAILS
    - Destination: {destination}
    - Duration: {days} days

    SPECIAL INTERESTS
    {interests_text}

    GUARDRAILS / CONSTRAINTS
    {guardrails_text}

    INSTRUCTIONS
    - Align activities strongly with selected interests.
    - Enforce guardrails with zero exceptions.
    - Keep the itinerary practical and well-paced.
    """).strip()

# -------------------------
# MODEL CALL WITH FALLBACK
# -------------------------
MODELS = ["gpt-5", "gpt-5-mini", "gpt-4.1"]

def extract_text(resp):
    try:
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""

def generate_plan(prompt):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for model in MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=2000,
            )
            text = extract_text(resp)
            if text:
                st.session_state["last_model_used"] = model
                return text
        except Exception:
            continue

    raise RuntimeError("All model attempts failed.")

# -------------------------
# PDF GENERATION
# -------------------------
def markdown_to_flowables(md, styles):
    flow = []
    body = styles["BodyText"]
    h2 = ParagraphStyle("H2", parent=styles["Heading2"])
    h3 = ParagraphStyle("H3", parent=styles["Heading3"])

    for line in md.splitlines():
        if line.startswith("## "):
            flow.append(Spacer(1, 8))
            flow.append(Paragraph(line[3:], h2))
        elif line.startswith("### "):
            flow.append(Spacer(1, 6))
            flow.append(Paragraph(line[4:], h3))
        elif line.lstrip().startswith("-"):
            flow.append(Paragraph("• " + line.lstrip()[1:], body))
        elif line.strip():
            flow.append(Paragraph(line, body))
        else:
            flow.append(Spacer(1, 6))

    return flow

def write_pdf(md_text, filename="travel_plan.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Travel Guide Plan",
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=18)
    story.append(Paragraph("Personalized Travel Plan", title_style))
    story.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 12))

    story.extend(markdown_to_flowables(md_text, styles))
    doc.build(story)

    return filename

# -------------------------
# INPUT FORM
# -------------------------
with st.form("travel_form"):
    st.text_input(
        "1) Destination",
        placeholder="e.g., Rome, Italy",
        key="destination"
    )

    st.number_input(
        "2) Number of days",
        min_value=1,
        max_value=30,
        step=1,
        key="days"
    )

    st.multiselect(
        "3) Special Interests",
        options=INTEREST_OPTIONS,
        key="interests"
    )

    st.multiselect(
        "4) Guardrails / Constraints",
        options=GUARDRAIL_OPTIONS,
        key="guardrails"
    )

    submitted = st.form_submit_button("Generate Travel Plan")

# -------------------------
# MAIN ACTION
# -------------------------
if submitted:
    if not st.session_state["destination"]:
        st.warning("Please provide a destination.")
    else:
        with st.spinner("Creating your personalized travel itinerary..."):
            user_prompt = build_user_prompt(
                st.session_state["destination"],
                st.session_state["days"],
                st.session_state["interests"],
                st.session_state["guardrails"],
            )
            st.session_state["plan_md"] = generate_plan(user_prompt)

# -------------------------
# OUTPUT
# -------------------------
if st.session_state["plan_md"]:
    st.success("Travel plan generated!")
    st.caption(f"Model used: {st.session_state.get('last_model_used', 'unknown')}")

    st.subheader("📅 Your Travel Itinerary")
    st.markdown(st.session_state["plan_md"])

    with st.expander("Raw text (copy-friendly)"):
        st.text_area("Itinerary", st.session_state["plan_md"], height=400)

    try:
        pdf_path = write_pdf(st.session_state["plan_md"])
        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Download Travel Plan PDF",
                data=f.read(),
                file_name="travel_plan.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

st.divider()
st.button("🔁 Reset Form", on_click=reset_all)
