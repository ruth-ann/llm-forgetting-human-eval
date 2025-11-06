import streamlit as st
import pandas as pd
import random
from datetime import datetime
from github import Github

st.set_page_config(page_title="Human Evaluation", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("eval_pairs.csv")

df = load_data()

if "annotator" not in st.session_state:
    name = st.text_input("Please enter your name or code:")
    if not name:
        st.stop()
    annotator = "".join(name.split())[:8]
    st.session_state.annotator = annotator
annotator = st.session_state.annotator

if "i" not in st.session_state:
    st.session_state.i = 0

random.seed(annotator)
order = list(df.index)
random.shuffle(order)

st.title("Human Evaluation Task")
st.info("You will read two passages per example and decide which one is better written or conveys the meaning more clearly.")

i = st.session_state.i
if i >= len(order):
    st.success("✅ You’ve completed all evaluations. Thank you!")
    st.stop()

row = df.loc[order[i]]
flip = random.choice([True, False])
passage_left = row["passage_a"] if not flip else row["passage_b"]
passage_right = row["passage_b"] if not flip else row["passage_a"]

st.markdown(f"### Example {i+1} of {len(order)}")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Left Passage")
    st.write(passage_left)
with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)

choice = st.radio("Which passage is better?", ["Left", "Right", "Same quality"], horizontal=True)

if st.button("Next"):
    if not choice:
        st.warning("Please select an option before proceeding.")
        st.stop()

    if choice == "Left":
        final_choice = "A" if not flip else "B"
    elif choice == "Right":
        final_choice = "B" if not flip else "A"
    else:
        final_choice = "Same quality"

    new_row = {
        "timestamp": datetime.now().isoformat(),
        "annotator": annotator,
        "pair_id": row["id"],
        "choice": final_choice,
    }

    df_new = pd.DataFrame([new_row])
    file_path = f"results/{annotator}_responses.csv"

    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])

    try:
        repo_file = repo.get_contents(file_path)
        repo.update_file(file_path, f"Update {annotator} responses", df_new.to_csv(index=False), repo_file.sha)
    except:
        repo.create_file(file_path, f"Add {annotator} responses", df_new.to_csv(index=False))

    st.session_state.i += 1
    st.stop()

