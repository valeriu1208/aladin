import streamlit as st

#Crearem el titol de la página
ROLES = [None, "User", "Admin"]
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
initial_page = st.Page("initial.py", title = "Welcome", icon=":material/home:")
request_1 = st.Page(
    "request/map.py",
    title="Map",
    icon=":material/map:",
    default=(role == "User"),
) 
respond_1 = st.Page(
    "respond/chatbot.py",
    title="Chatbot",
    icon=":material/chat:",
    
)
admin_1 = st.Page(
    "admin/graficas.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
account_pages = [logout_page, settings]
request_pages = [initial_page,request_1,respond_1]
admin_pages = [admin_1]
st.logo("images/WZE.png",size = "large" , icon_image= None)
page_dict = {}
if st.session_state.role in ["User", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages
if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
    if st.session_state.login_state and st.session_state.role is None:
        st.write("You do not have access to any pages. Please contact the administrator.")
else:
        pg = st.navigation([st.Page(login_screen)])
pg.run()
