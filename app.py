import streamlit as st
from uuid import uuid4
import datetime as dt
from pyvis.network import Network
import streamlit.components.v1 as components
from sentence_transformers import SentenceTransformer, util

st.set_page_config(page_title="Sovereignty Knowledge Graph V2+", layout="wide")

# --- In-memory store ---
if "notes" not in st.session_state:
    st.session_state.notes = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = []

# --- Load sentence transformer model ---
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# --- Sidebar: New note input ---
st.sidebar.header("💡 Add a New Thought")
st.sidebar.markdown("Welcome! Share whatever idea is on your mind. Connect it with your existing notes naturally by tagging.")
new_title = st.sidebar.text_input("Title", placeholder="What's the essence of this thought?")
new_body = st.sidebar.text_area("Content", placeholder="Write your insight here...")
new_tags = st.sidebar.text_input("Tags (comma-separated)", placeholder="e.g., autonomy, energy, philosophy")

if st.sidebar.button("Save Note"):
    if new_title.strip() and new_body.strip():
        note_id = str(uuid4())
        st.session_state.notes.append({
            "id": note_id,
            "title": new_title.strip(),
            "body": new_body.strip(),
            "tags": [t.strip() for t in new_tags.split(',')] if new_tags else [],
            "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Compute embedding for the new note
        embedding = model.encode(new_body.strip(), convert_to_tensor=True)
        st.session_state.embeddings.append({'id': note_id, 'embedding': embedding})
        st.sidebar.success("Saved! Your thought has been added and analyzed for connections.")
    else:
        st.sidebar.error("Please provide both a title and some content.")

# --- Main display ---
st.title("🧠 Personal Sovereignty Knowledge Graph V2+")
st.markdown("Visual network of your ideas. Blue nodes are notes, orange diamonds are tags. New semantic links appear as dashed green edges.")

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

    # --- Semantic similarity edges ---
    # Compute similarity between notes using embeddings
    if len(st.session_state.notes) > 1:
        for i in range(len(st.session_state.embeddings)):
            for j in range(i+1, len(st.session_state.embeddings)):
                sim = util.pytorch_cos_sim(st.session_state.embeddings[i]['embedding'], st.session_state.embeddings[j]['embedding'])
                if sim >= 0.6:  # threshold for semantic similarity
                    net.add_edge(st.session_state.embeddings[i]['id'], st.session_state.embeddings[j]['id'], color='green', width=2, dashes=True)

    # Generate and display graph
    net.show('graph.html')
    HtmlFile = open('graph.html','r',encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=650)
