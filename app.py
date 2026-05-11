import streamlit as st 
from login import  mostrar_login
from vista_general import  mostrar_dashboard

st.set_page_config(layout="wide", page_title="SOROCARE")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    mostrar_login()
else: 
    mostrar_dashboard()

    
