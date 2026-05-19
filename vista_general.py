import streamlit as st
import requests
import pandas as pd

if 'pagina' not in st.session_state: 
    st.session_state.pagina = "Vivienda 1"

st.set_page_config(layout="wide", page_title="Sorocare")

def vista_datos():
    vivienda = st.session_state.get("vivienda_info",{})
    nombre_completo = st.session_state.get("usuario_nombre", "Usuario")

    vivienda_actual = st.session_state.pagina
    coords = {
        "Vivienda 1": "41.6444,-4.7288", 
        "Vivienda 2": "40.4167,-3.7033", 
        "Vivienda 3": "41.3851,2.1734"
    }
    punto_gps = coords.get(vivienda_actual, "41.6444,-4.7288")
    map_url = f"https://maps.google.com/maps?q={punto_gps}&z=15&output=embed"

    with st.container(key="auto"):
        col_datos, col_mapa = st.columns(2,border=True)
        
        with col_datos:
            st.markdown("<h3 style='text-align: center; color: black;'>Datos Usuario: </h3>", unsafe_allow_html=True)
            st.write(f"**Nombre:** {nombre_completo}")
            # Usamos los datos reales de la API
            st.write(f"**Población:** {vivienda.get('poblacion', 'N/A')}")
            st.write(f"**Municipio:** {vivienda.get('municipio', 'N/A')}")
            st.write(f"**Provincia:** {vivienda.get('provincia', 'N/A')}")
        with col_mapa:
            st.markdown("<h3 style='text-align: center; color: black;'>Mapa</h3>", unsafe_allow_html=True)
            # Mapa de ejemplo
            st.iframe(map_url, height="content")

def vista_mapa():
    st.subheader("Mapa con posible iframe", text_alignment="center")
            
MAPEO_CATEGORIAS = {
    "chatGPT": "Conversación",
    "arrastrar": "Otros",
    "ejercicio": "Ejercicios",
    "noticias": "Información",
    "calendario": "Utilidades",
    "radio": "Ocio",
    "musica": "Ocio",
    "goTo": "Otros",
    "juego": "Ocio",
    "seguir": "Otros",
    "chiste": "Ocio",
    "recetas": "Utilidades",
    "voz": "Otros",
    "curiosidad": "Información",
    "tiempo": "Información",
    "lista compra": "Utilidades",
    "saludo": "Otros",
    "fecha": "Otros",
    "lectura": "Ocio",
    "poesia": "Ocio",
    "podcast": "Ocio",
    "preguntas": "Información"
}   

def formatear_tiempo(tiempo_delta):
    # Si el tiempo es nulo o 0, devolvemos 0 segundos
    if pd.isnull(tiempo_delta) or tiempo_delta.total_seconds() == 0:
        return "0 segundos"

    # Extraemos los componentes del tiempo (días, horas, minutos, segundos)
    componentes = tiempo_delta.components
    dias = componentes.days
    horas = componentes.hours
    minutos = componentes.minutes
    segundos = componentes.seconds

    partes = []
    if dias > 0:
        partes.append(f"{dias} {'día' if dias == 1 else 'días'}")
    if horas > 0:
        partes.append(f"{horas} {'hora' if horas == 1 else 'horas'}")
    if minutos > 0:
        partes.append(f"{minutos} {'minuto' if minutos == 1 else 'minutos'}")
    if segundos > 0 and dias == 0 and horas == 0: # Para no ensuciar si ya hay horas
        partes.append(f"{segundos} {'segundo' if segundos == 1 else 'segundos'}")

    # Unimos las partes con "y" (Ej: 1 hora y 15 minutos)
    return " y ".join(partes)

def render_ocio(df_dia): 
    st.markdown("<h3 style='text-align: center;'>🎮 Actividades de Ocio</h3>", unsafe_allow_html=True)
    st.space()
    df_dia['duracion_td'] = pd.to_timedelta(df_dia['duracion'], errors='coerce')
    col1, col2 = st.columns(2)

    #---- JUEGOS ------#
    with col1: 
        st.markdown("#### Juegos")
        df_juegos = df_dia[df_dia['tipoEvento']=='juego'].copy()

        if not df_juegos.empty:
            tiempo_total = df_juegos['duracion_td'].sum()
            tiempo_bonito = formatear_tiempo(tiempo_total)
            st.info(f"**Tiempo total de juego:** {tiempo_bonito}")
            
            # Limpiamos para mostrar solo lo que importa y renombramos
            df_mostrar = df_juegos[['nombre', 'puntuacion', 'duracion']].copy()
            
            # Lógica de puntuación (-1 = No terminó)
            df_mostrar['puntuacion'] = df_mostrar['puntuacion'].apply(
                lambda x: "Abandonó" if str(x) == "-1" else x
            )
            df_mostrar.columns = ['Juego', 'Puntuación', 'Duración']
            st.dataframe(df_mostrar, width="stretch", hide_index=True)
        else:
            st.write("No jugó a nada hoy.")

    #----- musica y radio -----#
    with col2: 
        st.markdown("#### Música y Radio")
        df_audio = df_dia[df_dia['tipoEvento'].isin(['musica', 'radio', 'podcast'])].copy()
        
        if not df_audio.empty:
            tiempo_total = df_audio['duracion_td'].sum()
            tiempo_bonito = formatear_tiempo(tiempo_total)

            st.info(f"⏱️ **Tiempo total de escucha:** {tiempo_bonito}")
            
            # Agrupamos por tipo (música, radio...) y sumamos el tiempo
            resumen_audio = df_audio.groupby(['tipoEvento', 'nombre'])['duracion_td'].sum().reset_index()
            # Convertimos el timedelta a string para que se vea bonito en la tabla
            resumen_audio['duracion_td'] = resumen_audio['duracion_td'].astype(str).str.split('0 days ').str[-1]
            resumen_audio.columns = ['Tipo', 'Contenido / Emisora', 'Tiempo Total']
            
            st.dataframe(resumen_audio, width="stretch", hide_index=True)
        else:
            st.write("No escuchó nada hoy.")

    #----- lectura----#
    st.markdown("#### Lectura y Poesía")
    df_lectura = df_dia[df_dia['tipoEvento'].isin(['lectura', 'poesia'])].copy()
    if not df_lectura.empty:
        tiempo_total = df_lectura['duracion_td'].sum()
        tiempo_bonito = formatear_tiempo(tiempo_total)
        st.info(f"**Tiempo total de lectura:** {tiempo_bonito}")
        
        resumen_lectura = df_lectura[['tipoEvento', 'nombre', 'duracion']].copy()
        resumen_lectura.columns = ['Tipo', 'Título', 'Duración']
        st.dataframe(resumen_lectura, width="stretch", hide_index=True)
    else:
        st.write("No hubo lectura hoy.")

    #---- Total ocio ---#
    st.divider()
    total_ocio = df_dia['duracion_td'].sum()
    total_ocio_bonito = formatear_tiempo(total_ocio)
    st.success(f"**Tiempo total de Ocio:** {total_ocio_bonito}")

def render_utilidades(df_dia, user_id):
    st.markdown("<h3 style='text-align: center;'>🛠️ Utilidades</h3>", unsafe_allow_html=True)
    st.space()
    col_compra, col_recetas = st.columns(2)

    #---- lista de compras ----#

    with col_compra: 
        st.markdown("#### 🛒 Lista de la Compra")
        df_compra = df_dia[df_dia['tipoEvento'].str.lower() == 'lista compra']
        
        if not df_compra.empty:
            for idx, fila in df_compra.iterrows():
                st.checkbox(
                    label=fila['nombre'],
                    value=False,
                    key=f"chk_compra_{idx}"
                )
        else:
            st.info("No hay artículos en la lista hoy.")
    #---- recetas -----#
    with col_recetas: 
        st.markdown("#### 🍳 Recetas Vistas")
        df_recetas = df_dia[df_dia['tipoEvento'].str.lower() == 'recetas']
        
        if not df_recetas.empty:
            for _, fila in df_recetas.iterrows():
                st.markdown(f"-  **{fila['nombre']}**")
        else:
            st.info("No se buscaron recetas hoy.")
    st.divider()

    #------- Calendario ----#
    st.markdown("#### 📅 Calendario")
    url_agenda = f"http://127.0.0.1:8000/usuario/{user_id}/agenda"
    try: 
        respuesta = requests.get(url_agenda)
        if respuesta.status_code == 200: 
            datos_agenda = respuesta.json()

            if len(datos_agenda) > 0: 
                for evento in datos_agenda: 
                    titulo = evento.get('tituloTarea', '')
                    if titulo and titulo.startswith("0."):
                        titulo = titulo[2:]
                    st.markdown(f"- 🕒 {titulo}")
            else: 
                st.success("No hay eventos en la agenda para este usuario. ")
        else: 
            st.warning("No se pudo cargar la agenda")
    except requests.exceptions.ConnectionError:
        st.error("Error conectando con la API para la agenda.")

def renderizar_generico(df_dia, titulo):
    # Función "comodín" para las categorías que aún no tienen diseño específico
    st.markdown(f"<h3 style='text-align: center;'>📋 {titulo}</h3>", unsafe_allow_html=True)
    df_mostrar = df_dia[['tipoEvento', 'nombre', 'fechaRegistro']].copy()
    df_mostrar.columns = ['Actividad', 'Detalle', 'Hora']
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

def render_ejercicio(df_dia):
    st.markdown("<h3 style='text-align: center;'>💪 Resumen de Ejercicios</h3>", unsafe_allow_html=True)
    if df_dia.empty:
        st.info("No hay registros de ejrcicio para este dia")
        return
    df_ejercicio = df_dia.copy()
    df_ejercicio['duracion_td']= pd.to_timedelta(df_ejercicio['duracion'], errors="coerce")

    st.markdown("#### 🏋️‍♂️ Ejercicios Realizados")
    
    for _, fila in df_ejercicio.iterrows():
        # Ponemos la primera letra en mayúscula para que se vea bien (Ej: "Cuello")
        nombre_ejercicio = str(fila['nombre']).capitalize()
        
        # Formateamos el tiempo de ese ejercicio en concreto
        tiempo_individual = formatear_tiempo(fila['duracion_td'])
        
        # Verificamos si terminó (-1 = Empezado, 1 = Finalizado)
        estado = str(fila.get('puntuacion', ''))
        if estado == '1' or estado == '1.0':
            estado_texto = "Finalizado ✅"
        elif estado == '-1' or estado == '-1.0':
            estado_texto = "Solo empezado ⚠️"
        else:
            estado_texto = "Sin estado"

        # Pintamos el bulletpoint con Markdown
        st.markdown(
            f"<p style='font-size: 23px; margin-bottom: 10px;'>&bull; <b>{nombre_ejercicio}</b> ({tiempo_individual}) - <i>{estado_texto}</i></p>", 
            unsafe_allow_html=True
        )

    tiempo_total_crudo = df_ejercicio['duracion_td'].sum()
    tiempo_total_bonito = formatear_tiempo(tiempo_total_crudo)
    
    st.success(f"⏱️ **Tiempo total de ejercicio:** {tiempo_total_bonito}")

def render_informacion(df_dia):
    st.markdown("<h3 style='text-align: center;'>ℹ️ Resumen de Consultas e Información</h3>", unsafe_allow_html=True)
    
    if df_dia.empty:
        st.info("No hay registros de información para este día.")
        return

    df_info = df_dia.copy()
    df_info['duracion_td'] = pd.to_timedelta(df_info['duracion'], errors='coerce')
    
    # Definimos las subcategorías que queremos mapear internamente
    subcategorias = [
        {"id": "noticias", "titulo": "📰 Noticias ", "vacio": "No se consultaron noticias hoy."},
        {"id": "curiosidad", "titulo": "🧠 Curiosidades", "vacio": "No se buscaron curiosidades hoy."},
        {"id": "preguntas", "titulo": "❓ Preguntas", "vacio": "No se realizaron preguntas hoy."},
        {"id": "tiempo", "titulo": "☀️ Previsión del Tiempo", "vacio": "No se consultó el clima hoy."}
    ]
    
    # 2. Iteramos por cada bloque para calcular sus tiempos individuales y sus listas
    for subcat in subcategorias:
        # Filtramos pasándolo a minúsculas para que no falle por las mayúsculas de la API
        df_bloque = df_info[df_info['tipoEvento'].str.lower() == subcat["id"]]
        
        if not df_bloque.empty:
            # Sumamos el tiempo de este bloque en concreto y lo traducimos
            tiempo_bloque = df_bloque['duracion_td'].sum()
            tiempo_bloque_bonito = formatear_tiempo(tiempo_bloque)
            
            # Título de la subcategoría con su tiempo (Letra grande de 22px)
            st.markdown(
                f"<p style='font-size: 22px; font-weight: bold; margin-top: 18px; color: #1f80cf;'>{subcat['titulo']} —  {tiempo_bloque_bonito}</p>", 
                unsafe_allow_html=True
            )
            
            # Listamos cada consulta individual realizada en este bloque (Letra de 19px)
            for _, fila in df_bloque.iterrows():
                detalle = fila['nombre'] if fila['nombre'] else "Consulta general"
                st.markdown(
                    f"<p style='font-size: 19px; margin-left: 20px; margin-bottom: 6px;'>&bull; {detalle}</p>", 
                    unsafe_allow_html=True
                )
        else:
            # Si quieres que no aparezcan los bloques vacíos para ahorrar espacio, deja esto como 'pass'
            # Si prefieres que Celia sepa que no se usó, descomenta la línea de abajo:
            # st.markdown(f"<p style='font-size: 18px; color: gray; margin-left: 20px;'>{subcat['vacio']}</p>", unsafe_allow_html=True)
            pass

    st.divider()
    total_info_crudo = df_info['duracion_td'].sum()
    total_info_bonito = formatear_tiempo(total_info_crudo)
    
    st.success(f"🏆 **TIEMPO TOTAL INVERTIDO EN INFORMACIÓN HOY:** {total_info_bonito}")


def vista_actividad():
    st.subheader("Registro de Actividades", text_alignment="center")
    
    vivienda_data = st.session_state.get("vivienda_info", {})
    id_vivienda = vivienda_data.get("id", "No asignada")

    if not id_vivienda: 
        st.warning("No se ha encontrado el identificador de la vivienda. ")
        return
    try: 
        url_api = f"http://127.0.0.1:8000/vivienda/{id_vivienda}/actividad"
        respuesta = requests.get(url_api)

        if respuesta.status_code == 200:
            datos_actividad = respuesta.json()

            if len(datos_actividad) > 0:
                df_base = pd.DataFrame(datos_actividad)

                user_id = st.session_state.get('user_id')
                if not user_id:
                    user_id = 208
                
                df_base = df_base[df_base['userId'] == user_id]

                if df_base.empty:
                    st.info("No hay actividad registrada para tu usuario hoy.")
                    return

                df_base['fecha_dt'] = pd.to_datetime(df_base['fechaRegistro'])
                df_base['Fecha_Filtro'] = df_base["fecha_dt"].dt.date
                df_base['Categoria'] = df_base['tipoEvento'].str.lower().map(MAPEO_CATEGORIAS).fillna("Otros")

                dias_disponibles = sorted(df_base["Fecha_Filtro"].unique(), reverse=True)
                categorias_disponibles = sorted(df_base['Categoria'].unique())

                col_filtro_dia, col_filtro_cat = st.columns(2)

                with col_filtro_dia:
                    dia_elegido = st.selectbox("¿De qué día quieres ver la actividad?", options=dias_disponibles)
                
                with col_filtro_cat:
                    cat_elegida = st.selectbox("¿Qué actividad quieres buscar?", options=categorias_disponibles)

                df_filtrado = df_base[(df_base["Fecha_Filtro"]==dia_elegido) & (df_base['Categoria']==cat_elegida)].copy()
                
                st.divider()

                if cat_elegida == "Ocio":
                    render_ocio(df_filtrado)
                elif cat_elegida == "Utilidades":
                    render_utilidades(df_filtrado, user_id)
                elif cat_elegida == "Información":
                    render_informacion(df_filtrado)
                elif cat_elegida == "Ejercicios":
                    render_ejercicio(df_filtrado)
                else:
                    renderizar_generico(df_filtrado, "Otras Actividades")  
                     
            else: 
                st.info("No hay actividad registrada para el robot de esta vivienda.")
        else: 
            try: 
                mensaje_error = respuesta.json().get("detail", "Error desconocido en la API")
            except: 
                mensaje_error = "El servidor no respondio con un formato valido. "
            st.error(f"Error {respuesta.status_code}: {mensaje_error}")
    except requests.exceptions.ConnectionError:
         st.error("No se pudo conectar con el servicio web (Uvicorn)")

### CSS 
st.markdown("""
    <style>

            
    /*----HEADER ----*/ 
    header[data-testid="stHeader"] {
        /*opacity: 0; */
        visibility: hidden;
        transition: opacity .3s ease;
    }

    header[data-testid="stHeader"]:hover {
        opacity: 1;
    }
    .stMainBlockContainer {
        padding-top: 0rem !important;
    }  
    
    .stApp {
        background: linear-gradient(145deg, #43b9e8 0%, #c8d9e0 90%) !important;
    }
    
    .st-key-header{
        background-color: rgba(174, 217, 235, 0.8) !important; 
        padding: 15px 20px !important;
        border-radius: 5px;
        border: 1px solid rgba(151, 192, 201, 0.2);
        margin-top: -3rem !important; 
        margin-bottom: 0rem !important;
        
        min-width: 100vw !important;
        position: relative !important; 
        left: 50%;
        transform: translateX(-50%) !important;
    }
    
    /*---------BOTON VIVIENDA --------*/ 
    button[data-testid="stPopoverButton"]  {
        border: none;
        background: transparent;
        color: #1f80cf;
        padding: 0 !important; 
        margin-top: 0.5rem;
        line-height: 1 !important;
    }
    .st-key-popover [data-testid="stPopover"] button p {
        font-size: 23px; 
    }
    [data-testid="stRadio"] label {
        display: flex !important;
        align-items: center !important; 
        margin-bottom: 5px !important; 
    }
            
    /*----------MAPA--------*/
    .st-key-auto{
        background-color: transparent;
        max-height: 100vh !important; 
        overflow-y:auto;
        
        min-width: 98vw !important;/* Casi todo el ancho de la pantalla */
        position: relative !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
    }
            
    /*---------COLUMNAS ------*/
    .st-key-auto [data-testid="stColumn"]{
        background-color: rgba(154, 206, 227, 0.6) !important;
        border: 1px solid rgba(151, 192, 201, 0.2);
        position: relative;
    }
    
            
    /* -------TABS DESIGN--------*/ 
    button[data-testid="stTab"] p {
        color: black !important;  
        
    }    
       
    button[aria-selected="true"] p {
        font-weight: bold !important;
        padding-left: 5px;
        padding-right: 5px;
        margin-right:3px;
        margin-left: 3px;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: black !important;
    }
          
    [data-testid="stMarkdownContainer"] > p {
        font-size: 23px;   
    }
    /* col usuario */
            
    .st-key-user_menu  {
        border: none !important;
        background: transparent !important;
        color: #1f80cf !important;
        padding-right: 0 !important;
        margin-left: auto;
        margin-bottom: -6px !important; /* Ajuste para pegarlo al perfil */
    }
    
    .st-key-user_menu button p {
        font-size: 20px !important;
        margin: 0 !important;
    }
    [id="gdg-overlay-1"] {
        font-size: 30px;        
    } 
    
    </style>
    """, unsafe_allow_html=True)

st.space()
##### HEADER ######
with st.container(key="header"):

    username = st.session_state.get("usuario_nombre", "Invitado")
    rol = st.session_state.get("perfil", "Sin Rol")

    col_vivienda,col_logo,col_usuario = st.columns([1,2,1], vertical_alignment="center")
    with col_logo: 
        st.markdown("<h1 style= 'text-align: center;margin-top:0px;padding-top:0;'>SOROCARE</h1>", unsafe_allow_html=True)

    with col_vivienda:
        vivienda_data = st.session_state.get("vivienda_info", {})
        id_vivienda = vivienda_data.get("id", "No asignada")

        nombre_dinamico = f"Vivienda: {id_vivienda}"

        with st.popover(f"{st.session_state.pagina}", on_change="rerun", key="popover"):
            opciones = [nombre_dinamico]
            seleccion = st.radio("Ir a:", opciones, label_visibility="collapsed")
            if seleccion != st.session_state.pagina:
                st.session_state.pagina = seleccion
                st.rerun()

    with col_usuario:
        with st.popover(f"👤 {username}", key="user_menu"):
            if st.button("Cerrar Sesión", type="primary", width="stretch"):
                st.session_state.autenticado = False
                st.rerun()
        
        st.markdown(f"""<p style="margin-top: -10px; font-size: 20px; margin-bottom: 10px; color: #1f80cf; ">Perfil: {rol} </p>""", unsafe_allow_html=True,text_alignment="right")
## TABS ## 

tab_datos, tab_mapa, tab_actividad = st.tabs(["Datos Vivienda", "Mapa", "Actividad"])

with tab_datos: 
    vista_datos()
    
with tab_mapa: 
    vista_mapa()

with tab_actividad: 
    vista_actividad()
