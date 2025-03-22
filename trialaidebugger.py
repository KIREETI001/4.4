from openai import OpenAI
import os
from pathlib import Path
import webbrowser
import re

# --- CONFIGURATION ---
client = OpenAI(api_key="s")  # Replace with your actual key
ENTRY_FILE = "C:/Users/kiree/OneDrive/Desktop/hackathon_2/index.html"
TEMP_FILE = "candidate_fix.html"
TEMP_LOG = "run_log.txt"
BACKUP_SUFFIX = ".bak"

# --- HELPERS ---
def clean_gpt_output(raw_code: str) -> str:
    """
    Removes triple backticks and optional language (like html) from GPT responses.
    """
    # Remove ```html or  from start and end if present
    cleaned = re.sub(r"^```(?:html)?\s*", "", raw_code.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned

def get_html_fix_from_gpt(user_feedback: str, full_code: str, error_note: str = "") -> str:
    system_prompt = (
        "Upon receiving the bug report in the index.html code, "
        "identify the part of the code that is causing the bug, "
        "and suggest improvements to fix the bug. "
        "While fixing the bug, retain all UI architecture design and only make changes to the bugged function."
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

    raw_output = response.choices[0].message.content.strip()
    return clean_gpt_output(raw_output)

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

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    user_feedback = input("📣 Enter user feedback for the HTML bug:\n> ")

    # ✅ Load HTML from the single file directly
    with open(ENTRY_FILE, "r", encoding="utf-8") as f:
        full_html = f.read()

    attempt = 1
    approved = False
    error_note = ""

    while not approved:
        print(f"\n🔁 Attempt {attempt}: Asking GPT for HTML fix...")
        gpt_html = get_html_fix_from_gpt(user_feedback, full_html, error_note)

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