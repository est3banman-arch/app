import streamlit as st
import pandas as pd

def mostrar_login():
    st.markdown("""
    <style>

    .stApp {
            margin-top: -4rem;
    }
        
    .st-key-nombre [data-testid="stMarkdownContainer"] p {
        font-size: 30px; 
    }
    .st-key-contrasenia [data-testid="stMarkdownContainer"] p {
        font-size: 30px;            
    }

    div [data-testid="stTextInputRootElement"] {
        height: 40px !important;             
    }            

    input {
        font-size: 20px !important; 
        background-color: red; 
    }    
    [data-testid="stHeadingWithActionElements"] > h2 {
        font-size: 45px;            
    }   
                
    </style>
    """,unsafe_allow_html=True)

    

    st.set_page_config(page_title="Login")

    st.header("SOROCARE", divider="rainbow", text_alignment="center")

    #st.menu_button("menu", "hola", type="primary")

    # 1. Entrada de usuario
    nombre = st.text_input("👤 Usuario", placeholder="Usuario", key="nombre")


    contrasenia = st.text_input("🔎︎ Contraseña", placeholder="Contraseña", type="password", key="contrasenia") 
    

    # 2. El boton del login que comprueba lo anterior 
    login=st.button("ACCEDER", type="secondary", use_container_width=True)

    if login:
        if nombre == "admin" and contrasenia == "1234":
            st.success(f"Bienvenido {nombre}!")
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = "Esteban Mantilla" ### se saca del token
            st.session_state.perfil = "Gestor" ### se saca del token 
            st.rerun()
        elif not nombre: 
            st.error("Introduce Usuario")
        elif not contrasenia: 
            st.error("Introduce Contraseña")
        else: 
            st.error("Usuario o contraseña incorrectos")
