import streamlit as st
import os
from datetime import datetime
import random
import pandas as pd

from textblob import TextBlob

# ========== Sentiment Analysis ==========
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "Positive 😊"
    elif polarity < -0.2:
        return "Negative 😔"
    else:
        return "Neutral 😐"

# ========== Helper Functions ==========
def load_entries(filter_mood=None, folder="journal_entries"):
    if not os.path.exists(folder):
        return []
    entries = []
    for file in sorted(os.listdir(folder), reverse=True):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if filter_mood:
                    first_line = content.splitlines()[0]
                    if f"Mood: {filter_mood}" not in first_line:
                        continue
                entries.append((file, content))
    return entries

def get_mood_history(folder="journal_entries"):
    if not os.path.exists(folder):
        return []
    history = []
    for file in sorted(os.listdir(folder)):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    mood_line = lines[0].strip()
                    date_line = lines[1].strip()
                    if mood_line.startswith("Mood:") and date_line.startswith("Date:"):
                        mood = mood_line.split(":", 1)[1].strip()
                        date = date_line.split(":", 1)[1].strip().split("_")[0]
                        history.append((date, mood))
    return history

def search_entries(query, folder="journal_entries"):
    results = []
    if not os.path.exists(folder):
        return results
    for file in sorted(os.listdir(folder), reverse=True):
        if file.endswith(".txt"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if query.lower() in content.lower():
                    results.append((file, content))
    return results

def mood_suggestions(mood):
    suggestions = {
        "Happy": "🎶(https://www.youtube.com/watch?v=8xg3vE8Ie_E)",
        "Sad": "💖(https://youtu.be/am5FI9DkO80?si=3RzfMcUTZ0Z5tH12)",
        "Anxious": "🌿(https://youtu.be/Tdt9sbqdfSU?si=xh6ew3dc7vGJ142C)",
        "Energetic": "💃(https://www.youtube.com/watch?v=pRpeEdMmmQ0)",
        "Other": "🧘 Try 5 minutes of journaling or a walk."
    }
    return suggestions.get(mood, suggestions["Other"])

# ========== Data Setup ==========
moods = {
    "Happy": "https://www.youtube.com/watch?v=8xg3vE8Ie_E",
    "Sad": "https://youtu.be/am5FI9DkO80?si=3RzfMcUTZ0Z5tH12",
    "Anxious": "https://youtu.be/Tdt9sbqdfSU?si=xh6ew3dc7vGJ142C",
    "Energetic": "https://www.youtube.com/watch?v=pRpeEdMmmQ0"
}

quotes = [
    "You’re doing better than you think. 🌈",
    "Take a breath. You’re allowed to rest. 🌬️",
    "Your feelings are valid. 💙",
    "This moment is part of your growth. 🌱"
]

prompts = [
    "What made you smile today?",
    "What’s weighing on your mind?",
    "Write a letter to your future self.",
    "Describe your perfect day."
]

# ========== Streamlit UI ==========
st.set_page_config(page_title="Moodify: Music & Journal", layout="centered")
st.title("🎵 Moodify - Your Music & Journal Companion")
st.markdown("Let your mood guide your music and your words. ✍️")

# === Mood Selection ===
mood = st.selectbox("How are you feeling today?", list(moods.keys()))
if mood:
    st.markdown(f"**Mood:** {mood}")
    st.markdown(f"[🎧 Open Music Recommendation]({moods[mood]})")
    st.markdown(f"🔊 **Mood Suggestion:** {mood_suggestions(mood)}")

# === Writing Prompt ===
st.subheader("✍️ Need a Prompt?")
if st.button("🎲 Feeling stuck? Get a writing prompt"):
    st.info(random.choice(prompts))

# === Journal Entry ===
st.subheader("📓 Write Your Journal Entry")
entry = st.text_area("Type your thoughts here...")

if entry:
    st.markdown("🧠 **AI Mood Summary**")
    mood_summary = analyze_sentiment(entry)
    st.info(f"Your entry feels: **{mood_summary}**")

# === Save Entry ===
if st.button("💾 Save Entry"):
    today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "journal_entries"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{today}_{mood}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Mood: {mood}\nDate: {today}\n\n{entry}")
    st.success("Your journal entry has been saved!")

# === Quote of the Moment ===
st.subheader("💬 Quote of the Moment")
st.markdown(random.choice(quotes))

# === Search ===
st.subheader("🔍 Search Journal Entries")
search_query = st.text_input("Type a keyword (e.g., stress, goal, happy)")

if search_query:
    found = search_entries(search_query)
    if found:
        st.success(f"Found {len(found)} matching entry(ies):")
        for file, content in found[:5]:
            st.markdown(f"**📅 {file.replace('_',' ').replace('.txt','')}**")
            st.text_area("📝 Entry", content, height=150, key=file)
            st.markdown("---")
    else:
        st.warning("No matching entries found.")
else:
    # === View Past Entries ===
    st.subheader("📂 View Past Entries")
    filter_option = st.selectbox("🔍 Filter by mood?", ["All"] + list(moods.keys()))
    selected_mood = None if filter_option == "All" else filter_option
    entries = load_entries(filter_mood=selected_mood)

    if entries:
        for filename, content in entries[:5]:
            st.markdown(f"**🗓️ {filename.replace('_', ' ').replace('.txt','')}**")
            st.text_area("📝 Entry", content, height=150, key=filename)
            st.markdown("---")
    else:
        st.info("No journal entries found yet.")

# === Mood Graph ===
st.subheader("📊 Mood History Graph")
history = get_mood_history()

if history:
    df = pd.DataFrame(history, columns=["Date", "Mood"])
    mood_counts = df.groupby(["Date", "Mood"]).size().unstack(fill_value=0)
    st.line_chart(mood_counts)
else:
    st.info("Not enough data to plot yet. Write a few entries first!")
