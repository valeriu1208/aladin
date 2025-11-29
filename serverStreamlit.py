#En aquest arxiu definirem el visualitzador que en aquest cas es tracta de Streamlits on podrem veure l'informació d'una manera senzilla

#Definirem les llibreries en qüestió de streamlit i requests
import streamlit as st
import requests
import base64

#Crearem el titol de la página
ROLES = [None, "Requester", "Responder", "Admin"]
def login_screen():
    st.header("This app is private. Please log in to continue.")
    st.button("Log In with google", on_click=st.login)
    st.session_state.login_state = st.user.is_logged_in

def selctrole():
    st.header("Select your role:")
    role = st.selectbox("Role", ROLES) 
    if(st.button("Set Role")):
        st.session_state.role = role
        st.rerun()
def Log0ut():
    st.header("Log Out")
    if st.button("Log Out"):
        st.write("Are you sure you want to log out?")
        if st.button("Confirm Log Out",on_click=st.logout):
            st.session_state.role = None
            st.rerun()
        if st.button("Cancel"):
            st.rerun()

if "role" not in st.session_state:
        st.session_state.role = None
role = st.session_state.role

if not st.user.is_logged_in:
     pg =st.navigation([st.Page(login_screen)])
     pg.run()
     st.stop()
     
st.session_state.login_state = True
if st.user.is_logged_in:
    st.header(f"Welcome, {st.user.name}!")
    if st.session_state.role is None:
        selctrole()
        st.stop()
logout_page = st.Page(Log0ut, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
chatbot_page = st.Page("chatbot.py", title="Chatbot", icon=":material/chat:")
Map_page = st.Page("map.py", title="Map", icon=":material/map:")
request_1 = st.Page(
    "request/request_1.py",
    title="Request 1",
    icon=":material/help:",
    default=(role == "Requester"),
)    
request_2 = st.Page(
    "request/request_2.py", 
    title="Request 2", 
    icon=":material/bug_report:"
)
respond_1 = st.Page(
    "respond/respond_1.py",
    title="Respond 1",
    icon=":material/healing:",
    default=(role == "Responder"),
)
respond_2 = st.Page(
    "respond/respond_2.py",
     title="Respond 2",
     icon=":material/handyman:"
)
admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page(
    "admin/admin_2.py", 
    title="Admin 2", 
    icon=":material/security:"
)
account_pages = [logout_page, settings, chatbot_page, ]
request_pages = [request_1, request_2, Map_page]
respond_pages = [respond_1, respond_2]
admin_pages = [admin_1, admin_2]
st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")
page_dict = {}
if st.session_state.role in ["Requester", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role in ["Responder", "Admin"]:
    page_dict["Respond"] = respond_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages
if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
    if st.session_state.login_state and st.session_state.role is None:
        st.write("You do not have access to any pages. Please contact the administrator.")
else:
        pg = st.navigation([st.Page(login_screen)])
pg.run()
