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
        if os.path.exists(existing_file):
            prev_df = pd.read_csv(existing_file)
            st.session_state.i = len(prev_df)
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
st.info("Select a bucket for the Left Passage. The Right Passage will automatically get the opposite bucket. Press 'Next' to advance or 'Exit' to save progress and leave.")

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
    bucket_choice = st.radio("Assign to bucket:", ["Bucket 1", "Bucket 2"], horizontal=True)

with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)
    st.markdown("_Automatically assigned the opposite bucket_")

if st.button("Next"):
    if not bucket_choice:
        st.warning("Please select a bucket for the Left Passage before advancing.")
    else:
        final_left = bucket_choice
        final_right = "Bucket 2" if bucket_choice == "Bucket 1" else "Bucket 1"

        new_row = {
            "timestamp": datetime.now().isoformat(),
            "annotator": annotator,
            "pair_id": row["id"],
            "left_passage_bucket": final_left,
            "right_passage_bucket": final_right,
        }

        df_new = pd.DataFrame([new_row])
        os.makedirs("results", exist_ok=True)
        file_path = f"results/{annotator}_responses.csv"
        df_new.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)

        st.session_state.i += 1

if st.button("Exit and continue later"):
    st.success("Progress saved. You can return later to continue.")
    st.stop()

