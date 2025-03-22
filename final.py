import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from pathlib import Path
import webbrowser
from openai import OpenAI
import urllib.parse
from sqlalchemy import create_engine

# --- CONFIG ---
username = 'root'
password = urllib.parse.quote_plus('Apple2015*')
host = 'localhost'
port = '3306'
database = 'twitter_feedback_db'
TABLE_NAME = 'twitter_feedback'
ENTRY_FILE = "/Users/ziyang/Desktop/hackathon_2/index.html"
TEMP_FILE = "candidate_fix.html"
TEMP_LOG = "run_log.txt"
BACKUP_SUFFIX = ".bak"
API_KEY = ""

client = OpenAI(api_key=API_KEY)

# --- TEXT CLEANING ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

# --- TF-IDF KEY PHRASE EXTRACTION ---
def extract_summary_sentence(df):
    df['cleaned'] = df['content'].apply(clean_text)
    vectorizer = TfidfVectorizer(ngram_range=(2, 5), stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(df['cleaned'])

    sum_scores = tfidf_matrix.sum(axis=0)
    phrase_scores = [(phrase, sum_scores[0, idx]) for phrase, idx in vectorizer.vocabulary_.items()]
    phrase_scores.sort(key=lambda x: x[1], reverse=True)

    threshold = 0.05
    top_score = phrase_scores[0][1] if phrase_scores else 0
    grouped_phrases = [phrase for phrase, score in phrase_scores if abs(score - top_score) <= threshold]

    if grouped_phrases:
        return ', '.join(grouped_phrases).capitalize() + '.'
    else:
        return 'No significant key phrases found.'

# --- GPT FIX HANDLER ---
def clean_gpt_output(raw_code: str) -> str:
    cleaned = re.sub(r"^```(?:html)?\s*", "", raw_code.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned

def get_html_fix_from_gpt(user_feedback: str, full_code: str, error_note: str = "") -> str:
    system_prompt = (
        "Upon receiving the bug report in the index.html code, identify the part of the code that is causing the bug, "
        "and suggest improvements to fix the bug. While fixing the bug, retain all UI architecture design and only make changes to the bugged function."
    )

    error_section = f"Visual or structural error:\n{error_note}\n\n" if error_note else ""

    user_prompt = (
        "Bug Report:\n" + user_feedback + "\n\n" +
        error_section +
        "Here is the full content of index.html:\n\n" +
        full_code + "\n\n"
        "Please fix the HTML code directly and return the updated HTML code only — no explanation."
    )

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )

    return clean_gpt_output(response.choices[0].message.content.strip())

def save_code(filename: str, code: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

def open_in_browser(file_path: str):
    abs_path = os.path.abspath(file_path)
    webbrowser.open(f"file://{abs_path}")

def wait_for_developer_approval(file_path: str) -> bool:
    print(f"\n🚀 Candidate fix saved at: {file_path}")
    print("🌐 Opening it in your browser...")
    open_in_browser(file_path)

    print("🧑‍💻 Approve this fix and replace the original? [y/n]")
    while True:
        response = input("> ").strip().lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print("Please enter 'y' to approve or 'n' to reject.")

def log_error(attempt: int, error_note: str):
    with open(TEMP_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n--- Attempt {attempt} ---\n{error_note}\n")

# --- MAIN ---
if __name__ == "__main__":
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')
    df = pd.read_sql(f'SELECT * FROM {TABLE_NAME}', con=engine)
    summary_sentence = extract_summary_sentence(df)

    print("\n🔑 Key Phrases Summary:")
    print(summary_sentence)

    with open(ENTRY_FILE, "r", encoding="utf-8") as f:
        full_html = f.read()

    attempt = 1
    approved = False
    error_note = ""

    while not approved:
        print(f"\n🔁 Attempt {attempt}: Asking GPT for HTML fix...")
        gpt_html = get_html_fix_from_gpt(summary_sentence, full_html, error_note)

        print("💾 Saving candidate fix...")
        save_code(TEMP_FILE, gpt_html)

        approved = wait_for_developer_approval(TEMP_FILE)
        if approved:
            print("✅ Developer approved. Integrating fix...")
            original_path = Path(ENTRY_FILE)
            backup_path = original_path.with_suffix(original_path.suffix + BACKUP_SUFFIX)
            os.rename(original_path, backup_path)
            os.rename(TEMP_FILE, ENTRY_FILE)
            print(f"🎉 Fix applied! Original backed up as: {backup_path}")
        else:
            print("❌ Fix rejected. Retrying...")
            error_note = input("📝 Optional: Describe why this version was rejected:\n> ")
            log_error(attempt, error_note)
            attempt += 1
