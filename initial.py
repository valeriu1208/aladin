import streamlit as st
import pickle
import os

FILE = "data.pkl"

def loadprev():
    if os.path.exists(FILE):
        with open(FILE, "rb") as f:
            return pickle.load(f)
    return []

def save_reviews(reviews):
    with open(FILE, "wb") as f:
        pickle.dump(reviews, f)

reviews = loadprev()

# Safety check (VERY recommended)
if not isinstance(reviews, list):
    reviews = [reviews]

st.write("Welcome to WZE web page, we hope that you enjoy the app!")
st.markdown(
    "<span style='color:green'>On the left side you will have all the different options to use</span>",
    unsafe_allow_html=True
)

review1 = st.text_input("Please leave your review here")

stars = st.slider("Rating ⭐️", 1,5,3)
text = str(stars)
review = st.user.name + " sended -> "  + review1 + " with " + text + "⭐️" 

if st.button("Submit review"):

        if review.strip():
            reviews.append(review)
            save_reviews(reviews)
            st.success("Saved, thanks!")
            st.success(f"You've sended {stars} ⭐️")
else:
    st.error("Please write something or select a star grade before submitting 😎")
