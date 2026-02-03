# HW7-CareerCoach-AI-Project
# 🌍 AI Travel Guide Application

**Author:** Sajjad Cheema


## 1️⃣ Purpose

The **AI Travel Guide Application** is a Python-based project designed to solve a common travel-planning problem: creating a **personalized, realistic, and constraint-aware travel itinerary** without spending hours researching destinations, attractions, and logistics.

Instead of manually browsing blogs, maps, and reviews, this application leverages **AI-assisted planning** to:

* Understand a traveler’s destination, duration, interests, and constraints
* Enforce guardrails such as accessibility, budget, or activity level
* Generate a structured, day-by-day travel plan that is practical and well-paced

This project demonstrates how **Large Language Models (LLMs)** can be integrated into real-world workflows to act as intelligent assistants—augmenting human decision-making rather than replacing it.


## 2️⃣ What the Code Does

At a high level, the application:

* Provides a **Streamlit-based web interface** to collect user inputs such as destination, number of days, interests, and travel guardrails
* Uses **prompt engineering best practices** (system prompt + structured user prompt) to guide the AI toward consistent, high-quality outputs
* Calls OpenAI models with **automatic fallback logic**, ensuring reliability if one model is unavailable
* Generates a **Markdown-formatted itinerary** divided strictly by day, with morning, afternoon, and evening activities
* Converts the AI-generated itinerary into a **professionally formatted PDF** using ReportLab

### AI-Specific Logic

* A carefully crafted **system prompt** defines the AI’s role as an expert travel planner
* Guardrails are enforced explicitly in the prompt to ensure zero violations
* Interests and constraints directly influence the itinerary structure and activity selection
* Model fallback logic improves robustness and real-world usability


## 3️⃣ How to Run or Use

### Conceptual Usage

1. Launch the application
2. Enter your travel destination and number of days
3. Select your interests (e.g., museums, food, nature)
4. Apply guardrails (e.g., wheelchair accessible, kid-friendly)
5. Click **Generate Travel Plan**
6. Review the AI-generated itinerary on screen
7. Download a clean, printable PDF of your personalized travel plan

### Technical Setup (High-Level)

* Python 3.9+
* Install dependencies:

  * `streamlit`
  * `openai`
  * `python-dotenv`
  * `reportlab`
* Set your `OPENAI_API_KEY` in a `.env` file
* Run the app using:

  bash
  streamlit run Travel_guide.py
  


## 4️⃣ Why This Project Matters

This project showcases how **AI can be embedded into user-facing applications** to provide meaningful, customized outputs while respecting real-world constraints. It highlights practical skills in:

* Prompt engineering
* AI-assisted application design
* Responsible constraint enforcement
* End-to-end workflow automation

The Travel Guide app is not just a demo—it is a blueprint for building reliable, human-centered AI systems.

