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

# initialize session state
if "annotator" not in st.session_state:
    st.session_state.annotator = None
if "i" not in st.session_state:
    st.session_state.i = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "left_bucket" not in st.session_state:
    st.session_state.left_bucket = None
if "right_bucket" not in st.session_state:
    st.session_state.right_bucket = None

# enter name
if not st.session_state.annotator:
    name = st.text_input("Enter your name or code and press Enter:")
    if name:
        st.session_state.annotator = "".join(name.split())[:8]
    else:
        st.stop()

annotator = st.session_state.annotator

# shuffle order once per annotator
if "order" not in st.session_state:
    random.seed(annotator)
    st.session_state.order = list(df.index)
    random.shuffle(st.session_state.order)

i = st.session_state.i
if i >= len(df):
    st.success("✅ You’ve completed all evaluations. Thank you!")
    st.stop()

row = df.loc[st.session_state.order[i]]
flip = random.choice([True, False])
passage_left = row["passage_a"] if not flip else row["passage_b"]
passage_right = row["passage_b"] if not flip else row["passage_a"]

st.title("Human Evaluation Task")
st.info("Select a bucket for either passage. The other flips automatically. Press 'Next' to advance, 'Back' to go back, or 'Exit' to save progress.")

col1, col2 = st.columns(2)

def sync_buckets():
    if st.session_state.left_bucket == "Bucket 1":
        st.session_state.right_bucket = "Bucket 2"
    elif st.session_state.left_bucket == "Bucket 2":
        st.session_state.right_bucket = "Bucket 1"
    elif st.session_state.right_bucket == "Bucket 1":
        st.session_state.left_bucket = "Bucket 2"
    elif st.session_state.right_bucket == "Bucket 2":
        st.session_state.left_bucket = "Bucket 1"

with col1:
    st.markdown("#### Left Passage")
    st.write(passage_left)
    left = st.radio("Left Passage Bucket:", ["Bucket 1", "Bucket 2"],
                    index=0 if st.session_state.left_bucket == "Bucket 1" else 1 if st.session_state.left_bucket == "Bucket 2" else 0,
                    key="left_radio")
    st.session_state.left_bucket = left
    sync_buckets()

with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)
    right = st.radio("Right Passage Bucket:", ["Bucket 1", "Bucket 2"],
                     index=0 if st.session_state.right_bucket == "Bucket 1" else 1 if st.session_state.right_bucket == "Bucket 2" else 1,
                     key="right_radio")
    st.session_state.right_bucket = right
    sync_buckets()

def save_progress():
    new_row = {
        "timestamp": datetime.now().isoformat(),
        "annotator": annotator,
        "pair_id": row["id"],
        "left_passage_bucket": st.session_state.left_bucket,
        "right_passage_bucket": st.session_state.right_bucket
    }
    st.session_state.history.append(new_row)
    os.makedirs("results", exist_ok=True)
    file_path = f"results/{annotator}_responses.csv"
    pd.DataFrame([new_row]).to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Back"):
        if st.session_state.i > 0:
            st.session_state.i -= 1
            if st.session_state.history:
                last = st.session_state.history.pop()
                st.session_state.left_bucket = last["left_passage_bucket"]
                st.session_state.right_bucket = last["right_passage_bucket"]

with col2:
    if st.button("Next"):
        if st.session_state.left_bucket and st.session_state.right_bucket:
            save_progress()
            st.session_state.i += 1
            st.session_state.left_bucket = None
            st.session_state.right_bucket = None

with col3:
    if st.button("Exit and continue later"):
        st.success("Progress saved. You can return later to continue.")
        st.stop()

