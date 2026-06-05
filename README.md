# 🤖 Sorocare - Gestor de Automatizaciones (IoT Web App)
**Desarrollado por:** Esteban Caleb Mantilla Rodriguez

Interfaz web construida con **Streamlit** diseñada para la gestión, creación y monitorización de planes automatizados para asistencia robótica (Temi / Home Assistant). La aplicación actúa como un puente visual y amigable (Data-Driven UI) entre el usuario final y el backend domótico.

---

## 🏗️ Arquitectura y División del Proyecto

El proyecto sigue una estructura modular para separar la configuración, la autenticación y las vistas, permitiendo un mantenimiento escalable.

* `config.py`: Actúa como el centro de mando de las conexiones. Gestiona las URLs base de las APIs (ej. FastAPI en el puerto 8000 para usuarios/login y Flask en el puerto 5000 para el NUC/domótica).
* `vista_planes.py`: El núcleo del módulo de automatización. Contiene toda la lógica de lectura (GET), creación (POST) y borrado lógico (PATCH) de los planes programados.
* *(Otros archivos como `api.py`, `login.py`, etc.)*: Manejan la sesión del usuario (`st.session_state`), el enrutamiento de páginas y la seguridad general de la web.

---

## 🎨 Filosofía de Diseño: Lógica vs. Renderizado

Para mantener una estética minimalista, aprovechar el espacio negativo y evitar la sobrecarga visual del usuario, la aplicación implementa tres patrones de diseño fundamentales:

1.  **Data-Driven UI:** La interfaz de creación de planes no es estática. Se construye a sí misma dinámicamente leyendo el diccionario `CATALOGO_ACCIONES`. Solo se muestran los campos (inputs, sliders, toggles) estrictamente necesarios para la acción seleccionada.
2.  **Progressive Disclosure (Revelación Progresiva):** Los menús complejos se mantienen ocultos hasta que son relevantes. Por ejemplo, la configuración de un "sensor" solo aparece si el usuario selecciona explícitamente ese disparador.
3.  **Edición Contextual (Modo WhatsApp):** La tabla de visualización (`st.data_editor`) se mantiene en modo de "solo lectura parcial" por defecto. Las herramientas de borrado múltiple solo aparecen cuando el usuario activa el *Modo Edición*, previniendo clics accidentales y saltos bruscos en el layout.

---

## ⚡ Rendimiento y Gestión de Estado

Debido a la naturaleza reactiva de Streamlit (que recarga el script en cada interacción), se ha implementado un sistema estricto de caché:

* **`@st.cache_data(ttl=60)`:** Las peticiones GET a la base de datos se almacenan en memoria durante 60 segundos. Esto evita saturar el servidor con múltiples peticiones cuando el usuario navega entre pestañas.
* **Cache Invalidation:** Las funciones de escritura (POST, PATCH) incluyen el comando `.clear()` para "quemar" la memoria caché inmediatamente después de un éxito (201/200 OK). Seguido de un `st.rerun()`, garantiza que el usuario vea la tabla actualizada al milisegundo sin penalizar el rendimiento global.

---

## 🛠️ Guía de Expansión: Cómo añadir nuevas Acciones/Planes

El sistema está diseñado para escalar. Si el equipo de robótica desarrolla un nuevo *script* en el NUC (por ejemplo, encender luces), no es necesario reescribir toda la web. Sigue estos 3 pasos en `vista_planes.py`:

### Paso 1: Actualizar el Catálogo Maestro
Añade la nueva acción al diccionario `CATALOGO_ACCIONES`, especificando su nombre técnico (`tipo`) y qué variables necesita el servidor (`reqs`).

```python
CATALOGO_ACCIONES = {
    # ... planes existentes ...
    "💡 Encender Luces Salón": {
        "tipo": "BT_luces_on",
        "reqs": ["location", "color", "brillo"] # Nuevos requisitos
    }
}
