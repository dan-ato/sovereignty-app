import streamlit as st
from uuid import uuid4
import datetime as dt
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Sovereignty Knowledge Graph V2", layout="wide")

# --- In-memory store ---
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
st.title("Personal Sovereignty Knowledge Graph V2")
st.markdown("Visual network of notes and tags. Click nodes to explore content.")

# --- Search ---
query = st.text_input("Search Notes", "")

results = []
for n in st.session_state.notes:
    if query.lower() in n["title"].lower() or query.lower() in n["body"].lower():
        results.append(n)

st.subheader(f"Results ({len(results)})")
for n in results:
    with st.expander(f"{n['title']} — {n['timestamp']}"):
        st.write(n["body"])
        if n["tags"]:
            st.write("**Tags:** ", ", ".join(n["tags"]))

# --- Network Graph ---
if st.session_state.notes:
    net = Network(height="600px", width="100%", notebook=False)
    net.barnes_hut()

    # Add nodes for notes
    for note in st.session_state.notes:
        net.add_node(note['id'], label=note['title'], title=note['body'], color='lightblue', shape='dot')

    # Add nodes for tags and edges
    tags_set = set()
    for note in st.session_state.notes:
        for tag in note['tags']:
            if tag not in tags_set:
                net.add_node(tag, label=tag, color='orange', shape='diamond')
                tags_set.add(tag)
            net.add_edge(note['id'], tag)

    # Generate and display graph
    net.show('graph.html')
    HtmlFile = open('graph.html','r',encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=650)
