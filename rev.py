import streamlit as st
import pickle
import os

FILE = "data.pkl"
def loadprev():
    if os.path.exists(FILE):
        with open(FILE, "rb") as f:
            return pickle.load(f)
    return []
st.write("Welcome Admin, please review the Users info")
revies = loadprev()
if revies:
    for i, r in enumerate(revies, 1):
        st.write(f"{i}. {r}")
else:
    st.info("No reviews yet.")
if st.button("🚮 Delete reviews"):
    if os.path.exists(FILE):
        os.remove(FILE)
        st.success("ALl reviwes have been deleted")
        st.rerun()  

    else:
        st.error("No data was deleted")
