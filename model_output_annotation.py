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
    if st.button("Start"):
        st.session_state.annotator = "".join(name.split())[:8]
        st.session_state.i = 0
        st.experimental_rerun()
    st.stop()

annotator = st.session_state.annotator

if "i" not in st.session_state:
    st.session_state.i = 0

random.seed(annotator)
order = list(df.index)
random.shuffle(order)

st.title("Human Evaluation Task")
st.info("Click a bucket for the Left Passage; the Right Passage will be automatically assigned the opposite bucket.")

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
    if st.button("Assign Left → Bucket 1", key=f"left1_{i}"):
        final_left = "Bucket 1"
        final_right = "Bucket 2"
        save_and_advance(annotator, row["id"], final_left, final_right)

    if st.button("Assign Left → Bucket 2", key=f"left2_{i}"):
        final_left = "Bucket 2"
        final_right = "Bucket 1"
        save_and_advance(annotator, row["id"], final_left, final_right)

with col2:
    st.markdown("#### Right Passage")
    st.write(passage_right)
    st.markdown("_Automatically assigned based on Left Passage selection_

