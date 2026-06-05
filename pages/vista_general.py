# ==============================================================================
# 🚀 SOROCARE - Core API
# ==============================================================================
# Desarrollado por: Esteban Caleb Mantilla Rodriguez
# ==============================================================================
import streamlit as st
import requests
import datetime
import pandas as pd
from config import API_BASE_URL
from streamlit_calendar import calendar
import base64
import os


if 'pagina' not in st.session_state: 
    st.session_state.pagina = "Vivienda 1"

MAPEO_CATEGORIAS = {
    "chatgpt": "Conversación",
    "arrastrar": "Otros",
    "ejercicio": "Ejercicios",
    "noticias": "Información",
    "calendario": "Utilidades",
    "radio": "Ocio",
    "musica": "Ocio",
    "goto": "Otros",
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
            st.markdown("<h3 style='text-align: center; color: black;'>Usuario: </h3>", unsafe_allow_html=True)
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
    st.subheader("Plano interactivo de la vivienda", text_alignment="center")
    ruta_plano = "plano_casa.png"
    src_imagen = ""

    if os.path.exists(ruta_plano):
        with open(ruta_plano, "rb") as archivo_img:
            # Convertimos los bytes de la imagen a texto plano binario
            img_codificada = base64.b64encode(archivo_img.read()).decode("utf-8")
            # Creamos la URL de datos que el navegador entiende perfectamente
            src_imagen = f"data:image/png;base64,{img_codificada}"
    else:
        st.error("⚠️ Error: No se encuentra el archivo 'plano_casa.png' en la carpeta raíz del proyecto.")
        return
    
    codigo_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css">
        
        <style>
            :root {{
                --card-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
            }}

            #center-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        background-color: transparent;
        color: white;
        font-family: 'Roboto', sans-serif;
            }}

            .demo-badge {{ background-color: #ff9800; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; margin-bottom: 20px;}}

            /* 1. NUEVO CONTENEDOR: Se encarga de centrar todo en la pantalla */
            #center-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
            }}

            /* 2. LA MAGIA RESPONSIVE: Este contenedor ahora "abraza" a la imagen exactamente */
            #dashboard-container {{
                position: relative;
                display: inline-block; /* Hace que el contenedor se encoja al tamaño de la imagen */
            }}

            /* 3. LA IMAGEN: Dicta el tamaño máximo que puede ocupar */
            #plano-img {{
                display: block;
                max-width: 90vw;
                max-height: 70vh;
                width: auto;
                height: auto;
                border-radius: 15px;
                box-shadow: var(--card-shadow);
            }}

            /* 4. LA CAPA DE ICONOS: Ahora mide el 100% de la imagen, no de la pantalla */
            #elements-layer {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%; 
                height: 100%;
                pointer-events: none;
            }}

            /* El resto del CSS se queda igual */
            .element {{
                position: absolute;
                transform: translate(-50%, -50%);
                transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: auto;
            }}

            .avatar {{
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 50%;
                padding: 6px;
                box-shadow: var(--card-shadow);
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .avatar i {{ font-size: 40px; color: #1f80cf; }}
            .robot i {{ font-size: 35px; color: #00d4ff; }}

            .state-label {{
                background-color: rgba(0, 0, 0, 0.7);
                padding: 6px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                border: 1px solid #444;
            }}

            .state-icon i {{ font-size: 28px; transition: color 0.3s ease; }}
        </style>
    </head>
    <body>

        <div class="demo-badge">MODO DEMOSTRACIÓN (Simulando datos del Robot)</div>

        <div id="center-wrapper">
            <div id="dashboard-container">
                <img src="{src_imagen}" id="plano-img" alt="Plano de la casa">
                
                <div id="elements-layer">
                    <div id="sergio" class="element avatar" style="display: none;"><i class="mdi mdi-account-circle"></i></div>
                    <div id="robot" class="element avatar robot" style="display: none;"><i class="mdi mdi-robot"></i></div>
                    <div id="puerta_principal" class="element state-icon"><i class="mdi mdi-door-closed"></i></div>
                    <div id="ventana" class="element state-icon"><i class="mdi mdi-window-closed-variant"></i></div>
                    <div id="pir_pasillo" class="element state-icon"><i class="mdi mdi-motion-sensor"></i></div>
                    <div id="temp_pasillo" class="element state-label">--°C</div>
                </div>
            </div>
        </div>

        <script>
            // El script JS de Sergio se queda intacto aquí abajo...
            const posiciones = {{
                salon: {{ top: '25%', left: '33%' }},
                cocina: {{ top: '27%', left: '76%' }},
                dormitorio: {{ top: '80%', left: '33%' }},
                baño: {{ top: '78%', left: '76%' }},
                pasillo: {{ top: '53%', left: '50%' }}
            }};

            document.getElementById('puerta_principal').style.top = '53%';
            document.getElementById('puerta_principal').style.left = '16%';
            document.getElementById('ventana').style.top = '53%';
            document.getElementById('ventana').style.left = '87%';
            document.getElementById('pir_pasillo').style.top = '53%';
            document.getElementById('pir_pasillo').style.left = '22%';
            document.getElementById('temp_pasillo').style.top = '53%';
            document.getElementById('temp_pasillo').style.left = '30%';

            const estancias = ['salon', 'cocina', 'dormitorio', 'baño', 'pasillo'];

            function simularDatosDeCasa() {{
                const falsoJSON = {{
                    ubicacion_sergio: estancias[Math.floor(Math.random() * estancias.length)],
                    ubicacion_robot: estancias[Math.floor(Math.random() * estancias.length)],
                    puerta1: Math.random() > 0.5 ? 'on' : 'off',
                    ventana1: Math.random() > 0.5 ? 'on' : 'off',
                    pir1: Math.random() > 0.4 ? 'on' : 'off',
                    temperatura1: (15 + Math.random() * 15).toFixed(1)
                }};
                actualizarUI(falsoJSON);
            }}

            function actualizarUI(data) {{
                const sergio = document.getElementById('sergio');
                if (posiciones[data.ubicacion_sergio]) {{
                    sergio.style.display = 'flex';
                    sergio.style.top = posiciones[data.ubicacion_sergio].top;
                    sergio.style.left = posiciones[data.ubicacion_sergio].left;
                }}

                const robot = document.getElementById('robot');
                if (posiciones[data.ubicacion_robot]) {{
                    robot.style.display = 'flex';
                    robot.style.top = posiciones[data.ubicacion_robot].top;
                    robot.style.left = posiciones[data.ubicacion_robot].left;
                }}

                const pPrincipalIcono = document.getElementById('puerta_principal').querySelector('i');
                if (data.puerta1 === 'on') {{
                    pPrincipalIcono.className = 'mdi mdi-door-open';
                    pPrincipalIcono.style.color = '#FF0000';
                }} else {{
                    pPrincipalIcono.className = 'mdi mdi-door-closed';
                    pPrincipalIcono.style.color = '#00FF00';
                }}

                const ventanaIcono = document.getElementById('ventana').querySelector('i');
                if (data.ventana1 === 'on') {{
                    ventanaIcono.style.color = '#FF0000';
                }} else {{
                    ventanaIcono.style.color = '#00FF00';
                }}

                const pirIcono = document.getElementById('pir_pasillo').querySelector('i');
                if (data.pir1 === 'on') {{
                    pirIcono.style.color = '#FFEB3B';
                }} else {{
                    pirIcono.style.color = '#757575';
                }}

                const tPasillo = document.getElementById('temp_pasillo');
                const temp = parseFloat(data.temperatura1);
                tPasillo.innerText = temp + '°C';
                
                if (temp < 19) tPasillo.style.color = '#00E5FF';
                else if (temp > 26) tPasillo.style.color = '#FF0000';
                else tPasillo.style.color = '#FFFFFF';
            }}

            setInterval(simularDatosDeCasa, 3000);
            simularDatosDeCasa();
        </script>
    </body>
    </html>
    """

    st.iframe(codigo_html, height=900)
    
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
        df_juegos = df_dia[df_dia['tipoEvento'].str.lower()=='juego'].copy()

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
        df_audio = df_dia[df_dia['tipoEvento'].str.lower().isin(['musica', 'radio', 'podcast'])].copy()
        
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
    df_lectura = df_dia[df_dia['tipoEvento'].str.lower().isin(['lectura', 'poesia'])].copy()
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

### Editar para crear nuevos recordatorios en la agenda. 
@st.dialog("Nuevo Recordatorio")
def recordatorio(user_id):
    with st.form("form_nuevo_recordatorio", clear_on_submit=True):
        nombre = st.text_input("Titulo de la tarea")
        descripcion = st.text_input("Notas adicionales")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("📆 Fecha", value=datetime.date.today())
        with col2:
            hora = st.time_input("⏰ Hora de inicio", value=datetime.time(10, 0))

        # Botón de envío dentro del formulario
        enviar = st.form_submit_button("Guardar en la Agenda", type="primary", use_container_width=True)

    if enviar: 
        if not nombre: 
            st.error("Pon nombre a tu tarea")
            return
        nueva_tarea = {
            "userId": user_id,
            "tituloTarea": nombre,
            "descripcionTarea": descripcion,
            "fecha": fecha.strftime("%Y-%m-%d"), # Formato estándar para base de datos
            "horaInicio": hora.strftime("%H:%M:%S"),
            "recordatorioManual": 1 # Marcamos que es manual
        }

        url = f"{API_BASE_URL}/agenda/crear"
        try:
            res = requests.post(url, json=nueva_tarea)
            if res.status_code == 200:
                st.success("✅ Tarea guardada correctamente")
                st.rerun() # Recargamos para que aparezca en el calendario
            else:
                st.error("Error al guardar")
        except:
            st.error("No hay conexión con la API")

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
                st.markdown(f"<p style='font-size: 20px; margin-bottom: 8px;'>&bull; <b>{fila['nombre']}</b></p>", unsafe_allow_html=True)
        else:
            st.info("No se buscaron recetas hoy.")
    st.divider()

    #------- Calendario ----#
    st.markdown("#### 📅 Calendario")
    url_agenda = f"{API_BASE_URL}/usuario/{user_id}/agenda"
    try: 
        respuesta = requests.get(url_agenda)
        if respuesta.status_code == 200: 
            datos_agenda = respuesta.json() 
            
            opciones_calendario = {
                "headerToolbar": {
                    "left": "today prev,next", # Botones de Hoy, Atrás y Adelante
                    "center": "title",         # El mes y año en el centro
                    "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek", # Filtros: Mes, Semana, Día, Lista
                },
                "initialView": "dayGridMonth", # Vista por defecto al abrir
                "locale": "es",                # ¡Para que salga en español!
                "buttonText": {
                    "today": "Hoy",
                    "month": "Mes",
                    "week": "Semana",
                    "day": "Día",
                    "list": "Lista"
                },
                "height": 700,                 # Altura del calendario
            }
            css_calendario = """
            .fc .fc-toolbar-title {
                text-transform: capitalize !important;
            }
            .fc .fc-button-primary {
                background-color: #1f80cf !important;
                border-color: #1f80cf !important;
            }
            .fc .fc-button-primary:hover {
                background-color: #1565a0 !important; /* Un azul más oscuro al pasar el ratón */
                border-color: #1565a0 !important;
            }
            .fc .fc-button-primary:not(:disabled):active, 
            .fc .fc-button-primary:not(:disabled).fc-button-active {
                background-color: #0f4b78 !important; /* Azul más oscuro al hacer clic */
                border-color: #0f4b78 !important;
            }
            """

            calendar(events=datos_agenda, options=opciones_calendario, custom_css = css_calendario)

        else: 
            st.warning("No se pudo cargar la agenda")
    except requests.exceptions.ConnectionError:
        st.error("Error conectando con la API para la agenda.")

    if st.button("Agregar un recordatorio", type="secondary", key="agregar_recordatorio"):
        recordatorio(user_id)

def renderizar_generico(df_dia, titulo):
    # Función "comodín" para las categorías que aún no tienen diseño específico
    st.markdown(f"<h3 style='text-align: center;'>📋 {titulo}</h3>", unsafe_allow_html=True)
    df_mostrar = df_dia[['tipoEvento', 'nombre', 'fechaRegistro']].copy()
    df_mostrar.columns = ['Actividad', 'Detalle', 'Hora']
    st.dataframe(df_mostrar, width="stretch", hide_index=True)

def render_ejercicio(df_dia):
    st.markdown("<h3 style='text-align: center;'>💪 Resumen de Ejercicios</h3>", unsafe_allow_html=True)
    if df_dia.empty:
        st.info("No hay registros de ejercicio para este dia")
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

def render_conversacion(df_dia):
    st.markdown("<h3 style='text-align: center;'>💬 Interacciones con el Asistente</h3>", unsafe_allow_html=True)
    
    df_chat = df_dia[df_dia['tipoEvento'].str.lower() == 'chatgpt'].copy()
    
    if df_chat.empty:
        st.info("No hubo conversaciones con el asistente este día.")
        return

    # PREPARACIÓN DE DATOS
    df_chat['duracion_td'] = pd.to_timedelta(df_chat['duracion'], errors='coerce')
    df_chat['Hora'] = pd.to_datetime(df_chat['fechaRegistro']).dt.strftime('%H:%M:%S')
    df_chat = df_chat.sort_values(by='id', ascending=True).reset_index(drop=True)

    # AGRUPADOR DE CONVERSACIONES
    conversaciones = []
    conv_actual = []

    for index, row in df_chat.iterrows():
        conv_actual.append(row) # Metemos el mensaje actual en la "caja"
        
        # Si el semáforo marca fin de conversación (-1), cerramos la caja y la guardamos
        if str(row['puntuacion']) in ['-1', '-1.0']:
            conversaciones.append(pd.DataFrame(conv_actual))
            conv_actual = [] # Vaciamos la caja para la siguiente conversación
            
    # Por si la última conversación del día se quedó a medias y no le llegó el -1
    if conv_actual:
        conversaciones.append(pd.DataFrame(conv_actual))

    # 3. CÁLCULO DE MÉTRICAS PRINCIPALES
    num_conversaciones = len(conversaciones)
    tiempo_total_crudo = df_chat['duracion_td'].sum()
    
    # Prevenimos el error de dividir por cero
    if num_conversaciones > 0:
        tiempo_medio_crudo = tiempo_total_crudo / num_conversaciones
    else:
        tiempo_medio_crudo = pd.Timedelta(seconds=0)

    tiempo_total_bonito = formatear_tiempo(tiempo_total_crudo)
    tiempo_medio_bonito = formatear_tiempo(tiempo_medio_crudo)

    st.space()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"💬 **Total Conversaciones:**\n\n{num_conversaciones}")
        
    with col2:
        st.info(f"⏱️ **Tiempo Total:**\n\n{tiempo_total_bonito}")
        
    with col3:
        st.warning(f"⚖️ **Media por Conv:**\n\n{tiempo_medio_bonito}")

    st.divider()

    ### RENDERIZADO VISUAL: LOS DESPLEGABLES (Segundo plano)
    st.markdown("#### 📜 Registro de Mensajes (Detalle)")
    
    for i, df_conv in enumerate(conversaciones):
        # Sacamos los datos resumen de cada bloque de conversación
        hora_inicio = df_conv.iloc[0]['Hora']
        mensajes_count = len(df_conv)
        duracion_conv = formatear_tiempo(df_conv['duracion_td'].sum())
        
        # Título del desplegable
        titulo_expander = f"🗣️ Conversación {i+1} | Inicio: {hora_inicio} | Duración: {duracion_conv} | Mensajes: {mensajes_count}"
        
        with st.expander(titulo_expander):
            df_mostrar = df_conv[['Hora', 'nombre', 'duracion']].copy()
            df_mostrar.columns = ['Hora', 'Mensaje del Usuario', 'Duración']
            
            st.dataframe(df_mostrar, width="stretch", hide_index=True)

def vista_actividad():
    st.subheader("Registro de Actividades", text_alignment="center")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        user_id = 208

    try: 
        url_api  = f"{API_BASE_URL}/usuario/{user_id}/actividad"
        respuesta = requests.get(url_api)

        if respuesta.status_code == 200:
            datos_actividad = respuesta.json()

            if len(datos_actividad) > 0:
                df_base = pd.DataFrame(datos_actividad)

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
                elif cat_elegida == "Conversación":
                    render_conversacion(df_filtrado)
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

CATALOGO_ACCIONES = {
    "🗣️ Ir y dar un mensaje": {
        "tipo": "BT_move_dest_speak",
        "reqs": ["location", "speech", "volume"]
    },
    "🤖 Ir y conectar con ChatGPT": {
        "tipo": "BT_ChatGPT",
        "reqs": ["location", "speech", "volume", "user"]
    },
    "⏰ Despertar al usuario": {
        "tipo": "BT_despertar",
        "reqs": ["location", "volume"]
    },
    "🎮 Ejecutar actividad": {
        "tipo": "BT_ejecutar_actividad",
        "reqs": ["location", "activity", "other_info", "duration", "buscar", "preguntar", "base", "volume"]
    }
}

# Funciones cacheadas y diálogos
@st.cache_data(ttl=60)
def obtener_planes_cacheados(id_vivienda):
    url_lectura = f"http://localhost:5000/back_NUC/planes-programados?viviendaId={id_vivienda}"
    try:
        res = requests.get(url_lectura)
        if res.status_code == 200:
            return res.json().get("planes", [])
        return []
    except Exception:
        return []

@st.dialog("⚠️ Confirmar Nuevo Plan")
def dialogo_confirmacion(payload):
    st.write(f"Vas a programar al robot para el plan: **{payload['nombre']}**")
    st.write("Resumen técnico de la orden:")
    st.json(payload["accion"]) # Mostramos el JSON limpio para que confirme
    
    col1, col2 = st.columns(2)
    if col1.button("❌ Cancelar", use_container_width=True):
        st.rerun()
        
    if col2.button("✅ SÍ, CREAR PLAN", type="primary", use_container_width=True):
        url_crear = "http://localhost:5000/back_NUC/planes-programados"
        try:
            res = requests.post(url_crear, json=payload)
            if res.status_code == 201:
                st.success("¡Plan creado con éxito!")
                obtener_planes_cacheados.clear() # Quemamos el caché
                st.rerun() # Recargamos para ver la tabla actualizada
            else:
                st.error(f"Error del servidor: {res.text}")
        except Exception:
            st.error("No se pudo conectar con el servidor local.")

@st.dialog("⚠️ Confirmar Eliminación")
def dialogo_eliminar(ids_a_borrar, nombres_a_borrar):
    st.markdown("Vas a ocultar/eliminar los siguientes planes:")
    for nombre in nombres_a_borrar:
        st.markdown(f"- **{nombre}**")
        
    st.warning("Desaparecerán de esta lista, pero el registro se mantendrá en la base de datos de la UVa.")
    
    col1, col2 = st.columns(2)
    if col1.button("❌ Cancelar", width="stretch"):
        st.rerun()
        
    if col2.button("🗑️ SÍ, ELIMINAR", type="primary", width="stretch"):
        # Aquí recorremos los IDs y le mandamos al servidor que los pase a estado "eliminado"
        # (Ajusta la ruta PATCH o DELETE según lo que haya programado tu compañero)
        for plan_id in ids_a_borrar:
            url_patch = f"http://localhost:5000/back_NUC/planes-programados/{plan_id}/estado"
            payload = {"estado": "eliminado", "actualizadoPor": "Web"}
            requests.patch(url_patch, json=payload)
            
        st.success("✅ Planes eliminados con éxito")
        obtener_planes_cacheados.clear() # Quemamos caché para que desaparezcan
        st.rerun()

# La Vista Principal para creacion de planes 
def vista_planes():
    st.subheader("Gestor de Planes", text_alignment="center")
    id_vivienda = st.session_state.get("vivienda_info", {}).get("id", 167) 
    
    st.space("xsmall")
    # --- SECCIÓN: VISUALIZAR TABLA INTERACTIVA ---
    
    # El interruptor "WhatsApp" arriba a la derecha
    col_titulo, col_toggle = st.columns([6, 1])
    with col_titulo:
        st.markdown("### 📋 Planes Programados Activos")
    with col_toggle:
        modo_edicion = st.toggle("✏️ Editar", value=False)
    
    planes = obtener_planes_cacheados(id_vivienda)
    
    # Filtramos para no mostrar los que ya estén "eliminados" lógicamente
    planes_visibles = [p for p in planes if p.get("estado") != "eliminado"]
    
    if len(planes_visibles) > 0:
        filas_tabla = []
        for plan in planes_visibles:
            estado_bruto = plan.get("estado", "activo")
            
            # Construimos la fila base
            fila = {
                "ID": plan.get("idPlanProgramado"),
                "Activo": True if estado_bruto == "activo" else False,
                "Nombre": plan.get("nombre"),
                "Trigger Tipo": plan.get("triggerTipo", "Desconocido"),
                "Trigger Config": str(plan.get("triggerConfigJson", {})),
                "Acción": f"[{plan.get('btTopic', '').split('/')[-1]}]"
            }
            
            # Si el modo edición está encendido, inyectamos la columna de seleccionar
            if modo_edicion:
                fila["🗑️ Seleccionar"] = False
                
            filas_tabla.append(fila)
            
        df_original = pd.DataFrame(filas_tabla)
        
        # Configuramos las columnas dinámicamente
        config_columnas = {
            "ID": None, # Siempre oculto
            "Activo": st.column_config.CheckboxColumn("¿Activo?")
        }
        
        if modo_edicion:
            config_columnas["🗑️ Seleccionar"] = st.column_config.CheckboxColumn("Seleccionar")
            # En modo edición, bloqueamos el checkbox de 'Activo' para que no mezclen acciones
            columnas_bloqueadas = ["Activo", "Nombre", "Trigger Tipo", "Trigger Config", "Acción"]
        else:
            columnas_bloqueadas = ["Nombre", "Trigger Tipo", "Trigger Config", "Acción"]

        # Renderizamos el Editor
        df_editado = st.data_editor(
            df_original,
            column_config=config_columnas,
            disabled=columnas_bloqueadas,
            hide_index=True,
            use_container_width=True,
            key="editor_planes"
        )
        
        # --- LÓGICA DE BOTONES SEGÚN EL MODO ---
        if modo_edicion:
            # 1. Modo Edición Activo: Mostramos tu botón mágico
            seleccionados = df_editado[df_editado["🗑️ Seleccionar"] == True]
            num_sel = len(seleccionados)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # EL BOTÓN: Se desactiva si num_sel es 0 (Queda gris). Si es > 0, se pone rojo ("primary")
            if st.button(f"🗑️ Eliminar {num_sel} planes seleccionados", type="primary", disabled=(num_sel == 0), width="stretch"):
                ids = seleccionados["ID"].tolist()
                nombres = seleccionados["Nombre"].tolist()
                dialogo_eliminar(ids, nombres)
                
        else:
            # 2. Modo Normal: Solo vigilamos si cambian el Activo/Deshabilitado
            cambios = df_editado[df_editado["Activo"] != df_original["Activo"]]
            if not cambios.empty:
                fila_cambiada = cambios.iloc[0]
                nuevo_estado = "activo" if fila_cambiada["Activo"] else "deshabilitado"
                
                url_patch = f"http://localhost:5000/back_NUC/planes-programados/{fila_cambiada['ID']}/estado"
                requests.patch(url_patch, json={"estado": nuevo_estado, "actualizadoPor": "Web"})
                
                st.toast(f"✅ Plan '{fila_cambiada['Nombre']}' actualizado")
                obtener_planes_cacheados.clear()
                st.rerun()
                
    else:
        st.info("No hay planes programados para esta vivienda.")
    # --- SECCIÓN: CREAR PLAN (Data-Driven UI) ---
    st.divider()
    st.markdown("### ➕ Crear Nuevo Plan")

    nombre_plan = st.text_input("📝 Nombre del Plan", placeholder="Ej: Bingo de la tarde")

    col_izq, col_der = st.columns(2)
    
    with col_izq:
        
        # 1. Usamos HTML para poner el H4 y le quitamos el margen de abajo a la fuerza (-15px o lo que prefieras) 
        st.markdown("#### ¿Qué dispara este plan?")
        # 2. Usamos "collapsed" para que el radio no genere su propio hueco
        tipo_trigger = st.radio(
            label=f"", 
            options=["⏰ A una hora concreta", "🚨 Cuando un sensor salte"],
            label_visibility="collapsed" 
        )
        
        trigger_data = {}
        if tipo_trigger == "⏰ A una hora concreta":
            hora_plan = st.time_input("¿A qué hora?")
            trigger_data = {"tipo": "time", "hora": hora_plan.strftime("%H:%M:%S")}
        else:
            sensor_id = st.text_input("ID del Sensor", placeholder="Ej: binary_sensor.caida")
            estado_sensor = st.selectbox("Cambio a estado:", ["on", "off"])
            trigger_data = {"tipo": "state", "entity_id": sensor_id, "to": estado_sensor}
            
    with col_der:
        st.markdown("#### La Acción (Qué hará el robot)")
        accion_visual = st.selectbox("Selecciona la acción:", list(CATALOGO_ACCIONES.keys()))
        
        # Extraemos la info del diccionario
        accion_tecnica = CATALOGO_ACCIONES[accion_visual]["tipo"]
        reqs = CATALOGO_ACCIONES[accion_visual]["reqs"]
        
        # Variables inicializadas en vacío para que no den error si no se usan
        ubicacion = mensaje = actividad = info_extra = None
        buscar = preguntar = base = False
        duracion = 30
        volumen = 5
        
        # EL RENDERIZADO DINÁMICO DE LA INTERFAZ
        if "location" in reqs:
            ubicacion = st.selectbox("📍 Ubicación destino", ["mesa celia", "mesa sergio", "salon", "cocina"])
        if "speech" in reqs:
            mensaje = st.text_input("💬 Mensaje a decir", placeholder="Escribe el texto aquí...")
        if "activity" in reqs:
            actividad = st.selectbox("🎮 Tipo de Actividad", ["juegos", "estimulacion", "ejercicios"])
        if "other_info" in reqs:
            info_extra = st.text_input("🏷️ Tema / Extra", placeholder="Ej: banderas")
        if "duration" in reqs:
            duracion = st.number_input("⏱️ Duración (min)", min_value=1, value=30)
            
        # Agrupamos los interruptores (Toggles) si existen en los requisitos
        if any(k in reqs for k in ["buscar", "preguntar", "base"]):
            st.markdown("**Comportamiento Autónomo:**")
            if "buscar" in reqs: buscar = st.toggle("Buscar al usuario")
            if "preguntar" in reqs: preguntar = st.toggle("Preguntar al usuario antes")
            if "base" in reqs: base = st.toggle("Volver a la base al terminar")
            
        if "volume" in reqs:
            volumen = st.slider("🔊 Volumen del robot", 1, 10, 5)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- EL BOTÓN PARA DISPARAR EL POPUP ---
    if st.button("Guardar Plan", type="primary", use_container_width=True):
        if not nombre_plan:
            st.error("⚠️ Debes ponerle un nombre al plan.")
        elif tipo_trigger != "⏰ A una hora concreta" and not sensor_id:
            st.error("⚠️ Debes introducir el ID del sensor.")
        else:
            # Construimos el payload de la Acción dinámicamente
            accion_payload = {
                "tipo": accion_tecnica,
                "sender": "Administrador",
                "receiver": "Temi_UVA2"
            }
            if ubicacion: accion_payload["location"] = ubicacion
            if mensaje: accion_payload["speech"] = mensaje
            if "volume" in reqs: accion_payload["volume"] = volumen
            if "user" in reqs: accion_payload["user"] = "Usuario_Interactivo"
            
            # Si es el Jefe Final (Actividad)
            if accion_tecnica == "BT_ejecutar_actividad":
                accion_payload["activity"] = actividad
                accion_payload["other_info"] = info_extra
                accion_payload["duration"] = duracion
                accion_payload["buscar"] = str(buscar)
                accion_payload["preguntar_usuario"] = str(preguntar)
                accion_payload["base_carga"] = str(base)

            # Empaquetado final para el Backend
            payload_completo = {
                "viviendaId": id_vivienda,
                "nombre": nombre_plan,
                "estado": "activo",
                "mode": "single",
                "actualizadoPor": st.session_state.get("usuario_nombre", "Usuario1"),
                "trigger": trigger_data,
                "accion": accion_payload
            }
            
            # Lanzamos la ventana flotante
            dialogo_confirmacion(payload_completo)
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
    button[data-testid="stTab"]  {
        margin-right: 10px;
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
    
    /* boton de agregar recordatorio */

    .st-key-agregar_recordatorio button {
        border: 2px solid #1f80cf !important; /* Borde azul */
        color: #1f80cf !important;            /* Texto azul */
        background-color: white !important;   /* Fondo blanco */
        border-radius: 8px !important;        /* Forzamos que mantenga sus curvas */
    }
    
    .st-key-agregar_recordatorio button:hover {
        background-color: #e3efff !important; /* El fondo se vuelve azul */
        color: #1f80cf !important;             /* El texto se vuelve blanco */
    }
    [data-testid="stSliderThumbValue"]{
        font-size: 20px; 
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

tab_datos, tab_mapa, tab_actividad, tab_planes = st.tabs(["Datos Vivienda", "Mapa", "Actividad", "Planes"])

with tab_datos: 
    vista_datos()
    
with tab_mapa: 
    vista_mapa()

with tab_actividad: 
    vista_actividad()

with tab_planes:
    vista_planes()
