import streamlit as st
import subprocess
import json
import os
import sys

# Configuración de la interfaz
st.set_page_config(
    page_title="GitHub Repo Auditor",
    page_icon="🚀",
    layout="centered"
)

# --- DETECCIÓN ABSOLUTA DE NODE/NPM PORTÁTIL ---
# Localizamos la carpeta 'bin' o de scripts del entorno virtual de Python actual
path_binario = os.path.dirname(sys.executable)

# En servidores Linux (como Streamlit Cloud), nodejs-bin deja los ejecutables ahí
node_path = os.path.join(path_binario, "node")
npm_path = os.path.join(path_binario, "npm")

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS JS ---
if not os.path.exists("core_js/node_modules"):
    with st.spinner("Instalando librerías de Node.js por primera vez..."):
        # Ejecutamos usando la ruta absoluta calculada de NPM
        subprocess.run([npm_path, "install"], cwd="core_js", capture_output=True)

st.title("GitHub Repository Auditor 🚀")
st.write("Audita la calidad, actividad y salud de cualquier repositorio público de GitHub.")

st.markdown("---")

# 1. SECCIÓN DEL MODAL: Configuración segura del Token
st.subheader("1. Autenticación")

with st.popover("🔑 Configurar Token de GitHub (Recomendado)"):
    st.markdown("### ¿Por qué necesitas un token?")
    st.write(
        "Por defecto, la API de GitHub solo permite 60 consultas por hora por dirección IP. "
        "Si configuras tu propio Personal Access Token (PAT), tu límite sube a **5,000 consultas por hora**, "
        "permitiendo un análisis profundo."
    )
    
    with st.expander("¿Cómo obtener mi token gratis? Paso a paso"):
        st.markdown(
            """
            1. Inicia sesión en tu cuenta de **GitHub**.
            2. Haz clic en tu foto de perfil (arriba a la derecha) y ve a **Settings**.
            3. En el menú de la izquierda, baja y haz clic en **Developer settings**.
            4. Selecciona **Personal access tokens** -> **Tokens (classic)**.
            5. Haz clic en **Generate new token** -> **Generate new token (classic)**.
            6. Dale un nombre (ej: *Repo Auditor*) y **no marques ninguna casilla de permisos**.
            7. Al final haz clic en **Generate token**, copia el código (`ghp_...`) y pégalo abajo.
            """
        )
    
    token_usuario = st.text_input(
        "Introduce tu GitHub Token (classic):", 
        type="password",
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
    )
    
    if token_usuario:
        st.success("¡Token guardado localmente en la sesión!")

# Guardamos el token en el estado de la sesión
if token_usuario:
    st.session_state["github_token"] = token_usuario
else:
    st.session_state["github_token"] = None

if st.session_state["github_token"]:
    st.info("Estado: Conectado a GitHub mediante Token de Usuario (Límite: 5000 peticiones/h).")
else:
    st.warning("Estado: Modo invitado activo (Límite: 60 peticiones/h).")

st.markdown("---")

# 2. SECCIÓN DE BÚSQUEDA Y EJECUCIÓN
st.subheader("2. Analizar Repositorio")
url_repo = st.text_input("Introduce la URL del repositorio de GitHub:", placeholder="https://github.com/usuario/nombre-repositorio")

if st.button("Iniciar Auditoría 📊"):
    if not url_repo:
        st.error("Por favor, introduce una URL válida.")
    elif not url_repo.startswith("https://github.com/"):
        st.error("La URL debe empezar por https://github.com/")
    else:
        with st.spinner("Ejecutando lógica en JavaScript y consultando API de GitHub..."):
            try:
                token_envio = st.session_state["github_token"] if st.session_state["github_token"] else "null"
                path_bridge = os.path.join("core_js", "bridge.js")
                
                # Ejecutamos llamando directamente al binario absoluto de Node
                resultado_proceso = subprocess.run(
                    [node_path, path_bridge, token_envio, url_repo],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Convertimos la salida JSON a un diccionario de Python
                metricas = json.loads(resultado_proceso.stdout)
                
                # 3. MOSTRAR RESULTADOS VISUALES
                st.success(f"¡Auditoría completada para **{metricas['nombre']}**!")
                
                if metricas['descripcion']:
                    st.markdown(f"**Descripción:** *{metricas['descripcion']}*")
                
                col1, col2, col3 = st.columns(3)
                col1.metric(label="⭐ Estrellas", value=metricas['estrellas'])
                col2.metric(label="🍴 Forks", value=metricas['forks'])
                col3.metric(label="⚠️ Issues Abiertos", value=metricas['issues_abiertos'])
                
                st.markdown("#### 📂 Información Adicional")
                st.write(f"📜 **Licencia:** {metricas['licencia']}")
                st.write(f"📅 **Creado el:** {metricas['creado_el'][:10]}")
                st.write(f"🔄 **Última actualización:** {metricas['updated_at'][:10]}")
                st.write(f"🔗 **URL de clonado:** `{metricas['url_clonado']}`")
                
            except subprocess.CalledProcessError as e:
                try:
                    error_json = json.loads(e.stderr)
                    st.error(f"Error en el analizador JS: {error_json.get('error', 'Desconocido')}")
                except Exception:
                    st.error(f"Error de sistema al ejecutar Node.js: {e.stderr if e.stderr else e.output}")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado en la interfaz: {str(e)}")
