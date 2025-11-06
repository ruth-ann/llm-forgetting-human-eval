import streamlit as st
import pandas as pd
import random
import os
import uuid
from datetime import datetime

st.set_page_config(page_title="Human Evaluation", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("eval_pairs.csv")

df = load_data()

if "annotator" not in st.session_state:
    st.session_state.annotator = str(uuid.uuid4())[:8]
annotator = st.session_state.annotator

random.seed(annotator)
order = list(df.index)
random.shuffle(order)

if "i" not in st.session_state:
    st.session_state.i = 0

st.title("Human Evaluation Task")
st.info("You will read two passages per example and decide which one is better written or conveys the meaning more clearly.")

i = st.session_state.i
if i >= len(order):
    st.success("✅ You’ve completed all evaluations. Thank you!")
    st.stop()

row = df.loc[order[i]]
st.markdown(f"### Example {i+1} of {len(order)}")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Passage A")
    st.write(row["passage_a"])
with col2:
    st.markdown("#### Passage B")
    st.write(row["passage_b"])

choice = st.radio("Which passage is better?", ["A", "B", "Same quality"], horizontal=True)

if st.button("Next"):
    os.makedirs("results", exist_ok=True)
    out_path = f"results/{annotator}_responses.csv"
    new_row = {
        "timestamp": datetime.now().isoformat(),
        "annotator": annotator,
        "pair_id": row["id"],
        "choice": choice,
    }
    pd.DataFrame([new_row]).to_csv(out_path, mode="a", header=not os.path.exists(out_path), index=False)
    st.session_state.i += 1
    st.experimental_rerun()







