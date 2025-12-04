import streamlit as st
from uuid import uuid4
import datetime as dt

st.set_page_config(page_title="Sovereignty Graph POC", layout="wide")

# --- In-memory store (replace later with a DB) ---
if "notes" not in st.session_state:
    st.session_state.notes = []

# --- Sidebar: New note input ---
st.sidebar.header("Add New Thought")
new_title = st.sidebar.text_input("Title")
new_body = st.sidebar.text_area("Content")
new_tags = st.sidebar.text_input("Tags (comma-separated)")

if st.sidebar.button("Save Note"):
    if new_title.strip() and new_body.strip():
        st.session_state.notes.append({
            "id": str(uuid4()),
            "title": new_title.strip(),
            "body": new_body.strip(),
            "tags": [t.strip() for t in new_tags.split(',')] if new_tags else [],
            "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.sidebar.success("Saved.")
    else:
        st.sidebar.error("Need both title and content.")

# --- Main display ---
st.title("Personal Sovereignty Knowledge Graph — POC")
st.markdown("This is the bare-bones functional skeleton: notes, tags, search, and simple linking.")

# --- Search Bar ---
query = st.text_input("Search Notes", "")

# --- Filter notes ---
results = []
for n in st.session_state.notes:
    if query.lower() in n["title"].lower() or query.lower() in n["body"].lower():
        results.append(n)

# --- Display results ---
st.subheader(f"Results ({len(results)})")
for n in results:
    with st.expander(f"{n['title']} — {n['timestamp']}"):
        st.write(n["body"])
        if n["tags"]:
            st.write("**Tags:** ", ", ".join(n["tags"]))

# --- Tag browser ---
all_tags = sorted({tag for n in st.session_state.notes for tag in n["tags"]})
st.subheader("Browse by Tag")
selected_tag = st.selectbox("Tag", [""] + all_tags)

if selected_tag:
    tagged = [n for n in st.session_state.notes if selected_tag in n["tags"]]
    st.write(f"### Notes tagged with '{selected_tag}' ({len(tagged)})")
    for n in tagged:
        with st.expander(n["title"]):
            st.write(n["body"])
