import streamlit as st
import subprocess
import json
import os
import sys

# Configuración de la interfaz visual
st.set_page_config(
    page_title="GitHub Repo Auditor",
    page_icon="🔍",
    layout="centered"
)

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS JS ---
if not os.path.exists("core_js/node_modules"):
    with st.spinner("Instalando dependencias de análisis..."):
        subprocess.run([sys.executable, "-m", "nodejs.npm", "install"], cwd="core_js", capture_output=True)

# Título principal
st.title("GitHub Repository Auditor")
st.write("Audita la calidad, actividad y salud de cualquier repositorio público de GitHub.")

st.markdown("---")

# 1. SECCIÓN: Autenticación
st.subheader("1. Autenticación")

with st.popover("🔑 Configurar Token de GitHub (Recomendado)"):
    st.markdown("### ¿Por qué necesitas un token?")
    st.write(
        "Por defecto, la API de GitHub limita mucho las consultas anónimas. "
        "Si usas tu token, aumentas tu límite un 8000%, permitiendo análisis "
        "más rápidos y detallados de los lenguajes y ramas."
    )
    
    with st.expander("¿Cómo obtener mi token gratis? Paso a paso"):
        st.markdown(
            """
            1. Inicia sesión en **GitHub** y ve a tu foto (arriba dcha) -> **Settings**.
            2. Menú izq -> **Developer settings** -> **Personal access tokens** -> **Tokens (classic)**.
            3. Haz clic en **Generate new token (classic)**, dale un nombre y **no marques ninguna casilla de permisos**.
            4. Copia el código (`ghp_...`) y pégalo abajo.
            """
        )
    
    token_usuario = st.text_input(
        "Introduce tu GitHub Token:", 
        type="password",
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
    )
    
    if token_usuario:
        st.success("¡Token guardado localmente en la sesión!")

if token_usuario:
    st.session_state["github_token"] = token_usuario
    st.info("Estado: Conectado mediante Token (Límite Alto).")
else:
    st.session_state["github_token"] = None
    st.warning("Estado: Modo invitado activo (Límite Bajo).")

st.markdown("---")

# 2. SECCIÓN DE BÚSQUEDA Y EJECUCIÓN
st.subheader("2. Analizar Repositorio")
url_repo = st.text_input("Introduce la URL:", placeholder="https://github.com/usuario/nombre-repositorio")

if st.button("Iniciar Auditoría 📊"):
    if not url_repo:
        st.error("Por favor, introduce una URL válida.")
    elif not url_repo.startswith("https://github.com/"):
        st.error("La URL debe empezar por https://github.com/")
    else:
        with st.spinner("Ejecutando lógica avanzada en JavaScript..."):
            try:
                token_envio = st.session_state["github_token"] if st.session_state["github_token"] else "null"
                path_bridge = os.path.join("core_js", "bridge.js")
                
                resultado_proceso = subprocess.run(
                    [sys.executable, "-m", "nodejs", path_bridge, token_envio, url_repo],
                    capture_output=True, text=True
                )
                
                if resultado_proceso.returncode != 0:
                    st.error("❌ El puente de JavaScript falló al ejecutarse:")
                    st.code(resultado_proceso.stderr if resultado_proceso.stderr else "Sin salida de error.")
                else:
                    try:
                        metricas = json.loads(resultado_proceso.stdout)
                        
                        st.success(f"¡Auditoría completada para **{metricas['nombre']}**!")
                        if metricas['descripcion']:
                            st.markdown(f"**Descripción:** *{metricas['descripcion']}*")
                        
                        # FILA 1: Métricas de Popularidad Base
                        st.markdown("#### 📈 Popularidad e Impacto")
                        c1, c2, c3 = st.columns(3)
                        c1.metric(label="⭐ Estrellas", value=f"{metricas['estrellas']:,}")
                        c2.metric(label="🍴 Forks", value=f"{metricas['forks']:,}")
                        c3.metric(label="👀 Seguidores (Watchers)", value=f"{metricas['seguidores_activos']:,}")
                        
                        # FILA 2: Métricas de Soporte y Comunidad (Métricas Nuevas)
                        st.markdown("#### 🛠️ Salud del Desarrollo y Soporte")
                        c4, c5, c6 = st.columns(3)
                        c4.metric(label="⚠️ Issues Abiertos", value=f"{metricas['issues_abiertos']:,}")
                        c5.metric(label="✅ Issues Solucionados", value=f"{metricas['issues_cerrados']:,}")
                        c6.metric(label="🔀 PRs Activos", value=metricas['prs_activos'])

                        # FILA 3: Estructura de Git
                        st.markdown("#### 📦 Peso y Estructura")
                        c7, c8 = st.columns(2)
                        
                        # Formatear el tamaño convenientemente (KB o MB)
                        size_kb = metricas['tamano_kb']
                        if size_kb > 1024:
                            size_display = f"{size_kb / 1024:.2f} MB"
                        else:
                            size_display = f"{size_kb} KB"
                            
                        c7.metric(label="💾 Tamaño en Disco", value=size_display)
                        c8.metric(label="🌿 Ramas Activas", value=metricas['ramas_activas'])

                        st.markdown("---")

                        # FILA 4: Desglose de Lenguajes
                        st.markdown("#### 💻 Desglose de Código")
                        col_lang_p, col_lang_d = st.columns([1, 2])
                        
                        with col_lang_p:
                            st.write("**Lenguaje Principal:**")
                            st.subheader(metricas['lenguaje_principal'])
                        
                        with col_lang_d:
                            st.write("**Uso de Lenguajes (Top):**")
                            dict_lenguajes = metricas['top_lenguajes']
                            if dict_lenguajes:
                                total_bytes = sum(dict_lenguajes.values())
                                contador = 0
                                for lang, bytes_used in sorted(dict_lenguajes.items(), key=lambda item: item[1], reverse=True):
                                    if contador >= 3: break
                                    porcentaje = (bytes_used / total_bytes) * 100
                                    st.write(f"{lang} ({porcentaje:.1f}%)")
                                    st.progress(int(porcentaje))
                                    contador += 1
                            else:
                                st.info("No se pudo desglosar el código.")

                        # FILA 5: Metadatos adicionales
                        st.markdown("#### 📂 Información Adicional")
                        st.write(f"📜 **Licencia:** {metricas['licencia']}")
                        st.write(f"📅 **Creado:** {metricas['creado_el'][:10]} | 🔄 **Actualizado:** {metricas['actualizado_el'][:10]}")
                        st.write(f"🔗 **Clonar:** `{metricas['url_clonado']}`")
                        
                    except json.JSONDecodeError:
                        st.error("❌ Error al procesar los datos estructurados del analizador.")
                        st.code(resultado_proceso.stdout)
                        
            except Exception as e:
                st.error(f"Ocurrió un error inesperado en la interfaz: {str(e)}")

# --- PIE DE PÁGINA (Desarrollado por José Luis Asenjo) ---
st.markdown("---")
footer_html = """
    <div style="text-align: center; color: gray; font-style: italic; padding-top: 20px;">
        Desarrollado por José Luis Asenjo.
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
