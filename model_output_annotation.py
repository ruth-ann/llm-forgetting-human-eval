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
                st.session_state.history = prev_df.to_dict('records')
            except pd.errors.ParserError:
                st.session_state.i = 0
                st.session_state.history = []
        else:
            st.session_state.i = 0
            st.session_state.history = []

if "annotator" not in st.session_state:
    st.text_input("Please enter your name or code and press Enter:", key="name_input", on_change=start_session)
    if "annotator" not in st.session_state:
        st.stop()

annotator = st.session_state.annotator

if "i" not in st.session_state:
    st.session_state.i = 0
if "history" not in st.session_state:
    st.session_state.history = []

random.seed(annotator)
order = list(df.index)
random.shuffle(order)

st.title("Human Evaluation Task")
st.info("Assign each passage to a bucket. Selecting one flips the other. Press 'Next' to advance, 'Back' to go to previous example, or 'Exit' to save and leave.")

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

if "selection" not in st.session_state:
    st.session_state.selection = None
if "bucket_choice" not in st.session_state:
    st.session_state.bucket_choice = None

if st.session_state.selection == "left":
    left_index = 0 if st.session_state.bucket_choice == "Bucket 1" else 1
    right_index = 1 - left_index
elif st.session_state.selection == "right":
    right_index = 0 if st.session_state.bucket_choice == "Bucket 1" else 1
    left_index = 1 - right_index
else:
    left_index = 0
    right_index = 1

with col1:
    st.markdown("#### Left Passage")
    st.write(passage_left)
    left_bucket = st.radio("Left Passage Bucket:", ["Bucket 1", "Bucket 2"], index=left_index, key="left_radio")

with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)
    right_bucket = st.radio("Right Passage Bucket:", ["Bucket 1", "Bucket 2"], index=right_index, key="right_radio")

if left_bucket != ("Bucket 1" if left_index == 0 else "Bucket 2"):
    st.session_state.selection = "left"
    st.session_state.bucket_choice = left_bucket
elif right_bucket != ("Bucket 1" if right_index == 0 else "Bucket 2"):
    st.session_state.selection = "right"
    st.session_state.bucket_choice = right_bucket

if st.button("Next"):
    if not st.session_state.bucket_choice:
        st.warning("Please select a bucket for one passage before advancing.")
    else:
        new_row = {
            "timestamp": datetime.now().isoformat(),
            "annotator": annotator,
            "pair_id": row["id"],
            "left_passage_bucket": st.session_state.bucket_choice if st.session_state.selection == "left" else ("Bucket 2" if st.session_state.bucket_choice == "Bucket 1" else "Bucket 1"),
            "right_passage_bucket": st.session_state.bucket_choice if st.session_state.selection == "right" else ("Bucket 2" if st.session_state.bucket_choice == "Bucket 1" else "Bucket 1"),
        }
        st.session_state.history.append(new_row)
        df_new = pd.DataFrame([new_row])
        os.makedirs("results", exist_ok=True)
        file_path = f"results/{annotator}_responses.csv"
        df_new.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)
        st.session_state.i += 1
        st.session_state.selection = None
        st.session_state.bucket_choice = None

if st.button("Back"):
    if st.session_state.i > 0:
        st.session_state.i -= 1
        if st.session_state.history:
            st.session_state.history.pop()
        st.session_state.selection = None
        st.session_state.bucket_choice = None

if st.button("Exit and continue later"):
    st.success("Progress saved. You can return later to continue.")
    st.stop()

