import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os

st.set_page_config(page_title="Human Evaluation", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("eval_pairs.csv")

df = load_data()

def start_session():
    name = st.session_state.name_input
    if name:
        st.session_state.annotator = "".join(name.split())[:8]
        existing_file = f"results/{st.session_state.annotator}_responses.csv"
        if os.path.exists(existing_file) and os.path.getsize(existing_file) > 0:
            try:
                prev_df = pd.read_csv(existing_file)
                st.session_state.i = len(prev_df)
            except pd.errors.ParserError:
                st.warning("Previous results file is corrupted. Starting fresh.")
                st.session_state.i = 0
        else:
            st.session_state.i = 0

if "annotator" not in st.session_state:
    st.text_input(
        "Please enter your name or code and press Enter:",
        key="name_input",
        on_change=start_session
    )
    if "annotator" not in st.session_state:
        st.stop()

annotator = st.session_state.annotator

if "i" not in st.session_state:
    st.session_state.i = 0

random.seed(annotator)
order = list(df.index)
random.shuffle(order)

st.title("Human Evaluation Task")
st.info("Assign each passage to a bucket. Selecting one automatically flips the other. Press 'Next' to advance or 'Exit' to save progress and leave.")

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

# Use session state to keep selections synced
if "left_bucket" not in st.session_state:
    st.session_state.left_bucket = None
if "right_bucket" not in st.session_state:
    st.session_state.right_bucket = None

with col1:
    st.markdown("#### Left Passage")
    st.write(passage_left)
    left_bucket = st.radio(
        "Left Passage Bucket:",
        ["Bucket 1", "Bucket 2"],
        index=0 if st.session_state.left_bucket == "Bucket 1" else 1 if st.session_state.left_bucket == "Bucket 2" else 0,
        key="left_radio"
    )

with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)
    right_bucket = st.radio(
        "Right Passage Bucket:",
        ["Bucket 1", "Bucket 2"],
        index=0 if st.session_state.right_bucket == "Bucket 1" else 1 if st.session_state.right_bucket == "Bucket 2" else 1,
        key="right_radio"
    )

# Sync the selections: changing one flips the other automatically
if left_bucket != st.session_state.left_bucket:
    st.session_state.left_bucket = left_bucket
    st.session_state.right_bucket = "Bucket 2" if left_bucket == "Bucket 1" else "Bucket 1"
elif right_bucket != st.session_state.right_bucket:
    st.session_state.right_bucket = right_bucket
    st.session_state.left_bucket = "Bucket 2" if right_bucket == "Bucket 1" else "Bucket 1"

if st.button("Next"):
    if not st.session_state.left_bucket:
        st.warning("Please select a bucket for one passage before advancing.")
    else:
        new_row = {
            "timestamp": datetime.now().isoformat(),
            "annotator": annotator,
            "pair_id": row["id"],
            "left_passage_bucket": st.session_state.left_bucket,
            "right_passage_bucket": st.session_state.right_bucket,
        }

        df_new = pd.DataFrame([new_row])
        os.makedirs("results", exist_ok=True)
        file_path = f"results/{annotator}_responses.csv"
        df_new.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)

        st.session_state.i += 1
        st.session_state.left_bucket = None
        st.session_state.right_bucket = None
        st.experimental_rerun()

if st.button("Exit and continue later"):
    st.success("Progress saved. You can return later to continue.")
    st.stop()

