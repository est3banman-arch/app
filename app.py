import streamlit as st 

st.set_page_config(layout="wide", page_title="SOROCARE")

login_page = st.Page("login.py", title="Login", url_path="login", visibility="hidden")
vista_general = st.Page("vista_general.py", title="Panel Sorocare", url_path="inicio", visibility="hidden")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    pg = st.navigation([login_page])
else: 
    pg = st.navigation([vista_general])
    
pg.run()

    
