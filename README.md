# 🧠 Team 4.4 – AI-Powered Feedback-to-Code Engine  
_24-Hour Project for iNTUition Hackathon 2025_

## 🚀 Overview

Our project aims to **redefine the software debugging and improvement process** using real-time user feedback, vectorized data analysis, and AI-powered code transformation. This proof-of-concept demonstrates how developers can receive *tested*, *relevant*, and *improvable* code suggestions based on user pain points—saving hours of manual debugging and user analytics.

## 🎯 Problem Statement

Developers often spend significant time:
- Sifting through user complaints or reviews,
- Identifying the root causes of bugs,
- Manually testing fixes,
- Iterating before arriving at a final, stable solution.

We wanted to change that—by letting AI do the heavy lifting.

---

## 🛠️ What We Built

This system simulates a full loop that:
1. **Collects and stores user feedback** in SQL format.
2. **Cleans and analyzes feedback** using Python (TF-IDF + clustering).
3. **Feeds structured prompts to OpenAI GPT** to:
   - Identify bugs,
   - Suggest code improvements,
   - Test the changes (simulated),
   - Provide suggested output.

4. **Developer Review UI:**
   - If the AI-suggested output meets expectations, the developer can **approve the code change with one click**.
   - Otherwise, the developer can **prompt the AI again** to refine the solution.

---

## 🧩 Key Technologies Used

| Layer                  | Stack/Tool                         |
|------------------------|------------------------------------|
| Feedback Storage       | SQL (simulated with Pandas + SQLite) |
| Data Cleaning & NLP    | Python (pandas, scikit-learn, nltk) |
| AI Integration         | OpenAI API (GPT-4)                 |
| Vectorisation & Clustering | TF-IDF, KMeans, Phrase Extraction |
| Code Suggestion Logic  | Prompt chaining with structured context |
| Developer Approval UI  | Command-line based / Scripted interaction (MVP)

---

## 🧠 How It Works

graph TD
    A[User Feedback (SQL)] --> B[Python Data Cleaning]
    B --> C[Vectorisation (TF-IDF)]
    C --> D[Clustering Common Issues]
    D --> E[Prompt to OpenAI GPT]
    E --> F[Code Bug Identified & Suggestion Generated]
    F --> G[Test Build and Output Simulation]
    G --> H[Display Suggested Output to Dev]
    H --> I[Update Source Code]
    H --> E

