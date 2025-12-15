import streamlit as st
st.write(f"Welcome to WZE web page,we hope that you enjoy the app!")
st.markdown(f"<span style='color:green'> On the left sider you will have all the different options to use</span>",
                unsafe_allow_html=True)
store = st.text_input("Please leave your reviews here")

