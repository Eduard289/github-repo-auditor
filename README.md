
# GitHub Repository Auditor

Una solución web híbrida y de alto rendimiento desarrollada para auditar la calidad, actividad, salud y estructura de cualquier repositorio público en GitHub. La aplicación combina la robustez y velocidad del ecosistema de Node.js para el consumo de la API REST de GitHub con la versatilidad de Streamlit (Python) para la orquestación del entorno en la nube y la visualización de datos en tiempo real.

**Desarrollado por José Luis Asenjo.**

---

## 🚀 Características Principales

* **Informe de Popularidad e Impacto:** Evaluación estricta de métricas de tracción social mediante el procesamiento de Estrellas, Forks y Seguidores Activos (*Watchers*).
* **Métricas de Salud del Desarrollo:** Cálculo avanzado del soporte histórico analizando la correlación entre *Issues* Abiertos, *Issues* Solucionados (Cerrados) y *Pull Requests* (PRs) activos en tiempo real.
* **Análisis de Infraestructura y Peso:** Mapeo del tamaño físico del repositorio en disco, implementando conversión automática inteligente a Kilobytes (KB) o Megabytes (MB).
* **Desglose Políglota de Código:** Extracción precisa de los volúmenes de bytes por lenguaje de programación, presentando un cálculo porcentual dinámico mediante barras de progreso nativas para los lenguajes predominantes.
* **Autenticación Adaptativa:** Sistema integrado de inyección de *Personal Access Tokens* (PAT) para conmutar dinámicamente entre el modo invitado (límite de 60 peticiones/hora) y el modo de alta tasa de transferencia (5,000 peticiones/hora).

---

## 🛠️ Arquitectura Tecnológica e Infraestructura

El núcleo de la aplicación implementa una arquitectura desacoplada y sin estado basada en dos capas tecnológicas principales:

1.  **Capa de Adquisición (Core JS):** Ubicada en `/core_js`, utiliza `@octokit/core` para comunicarse de manera eficiente con la API v3 de GitHub. Ejecuta tareas asíncronas concurrentes utilizando el bucle de eventos de Node.js para formatear e indexar la respuesta en un búfer JSON estructurado.
2.  **Capa de Presentación (App PY):** Ubicada en `/app_py`, utiliza Streamlit como servidor reactivo. En lugar de depender de binarios globales del sistema operativo, el entorno en la nube se autogestiona encapsulando un entorno Node.js portátil mediante `nodejs-bin`.

### Diagrama de Flujo de Datos

```text
[Usuario: URL Repo] -> [Interfaz Streamlit (Python)]
                             | (Invoca via sys.executable)
                             v
                     [bridge.js (Node.js)]
                             |
                    (API REST de GitHub v3)
                             |
                     [Retorno JSON Limpio]


### Estructura
github-repo-auditor/
├── app_py/
│   ├── app.py              # Interfaz gráfica y orquestador del subproceso Python
│   └── requirements.txt     # Dependencias de Python (Streamlit y nodejs-bin portátil)
├── core_js/
│   ├── github_analyzer.js   # Lógica pura de interacción asíncrona con Octokit
│   ├── bridge.js           # CLI Bridge que captura argumentos y exporta el JSON a Stdout
│   └── package.json         # Declaración de dependencias del ecosistema Node.js
└── README.md                # Documentación técnica del sistema


Clonar:
git clone [https://github.com/tu-usuario/github-repo-auditor.git](https://github.com/tu-usuario/github-repo-auditor.git)
cd github-repo-auditor


Instalar el entorno virtual y dependencias de Python:
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r app_py/requirements.txt

Ejecutar:
streamlit run app_py/app.py
                             

Despliegue en Producción (Streamlit Community Cloud)
Para desplegar esta aplicación en la nube de Streamlit de forma exitosa y libre de fallos de entorno, configure el formulario de la siguiente manera:

Repository: tu-usuario/github-repo-auditor

Branch: main

Main file path: app_py/app.py

El sistema se encargará de compilar los paquetes de Python, inyectará el módulo binario ejecutable de Node.js y aislará los procesos de red para garantizar la máxima privacidad del usuario durante las consultas.
                             
Este proyecto está bajo la Licencia MIT. Consulta el archivo de origen para obtener más detalles.
