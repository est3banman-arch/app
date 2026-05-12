import streamlit as st
import requests

def mostrar_login():
    st.markdown("""
    <style>

    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    .stMainBlockContainer {
        padding-top: 2rem !important;
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
        if not nombre: 
            st.error("Introduce Usuario")
        elif not contrasenia: 
            st.error("Introduce Contraseña")
        else: 
            try: 
                url_api = f"http://127.0.0.1:8000/usuario/{nombre}"
                respuesta = requests.get(url_api)

                if respuesta.status_code == 200: 
                    datos = respuesta.json()

                    st.success(f"Bienvenido {datos['nombre_completo']}!")
                    st.session_state.autenticado = True
                    st.session_state.usuario_nombre = datos['nombre_completo']
                    st.session_state.perfil = datos['rol']
                    st.session_state.vivienda_info = datos['vivienda']

                    st.rerun()
                else: 
                    try:
                        mensaje_error = respuesta.json().get("detail", "Error desconocido")
                    except:
                        mensaje_error = "La API dio un error pero no mandó detalles."

                    st.error(f"⚠️ Error {respuesta.status_code}: {mensaje_error}")

            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con el servicio web. ¿Has encendido uvicorn?")
            except Exception as e: 
                st.error(f"Ocurrio un error inesperado: {e}")

mostrar_login()

