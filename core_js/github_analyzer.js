import { Octokit } from "@octokit/core";

/**
 * Función principal para obtener las métricas básicas de un repositorio.
 * @param {string} token - El Personal Access Token de GitHub del usuario.
 * @param {string} repoUrl - La URL completa del repositorio (ej: "https://github.com/propietario/repo").
 */
export async function auditarRepositorio(token, repoUrl) {
    try {
        // 1. Limpiar la URL para extraer el propietario y el nombre del repositorio
        const urlLimpia = repoUrl.replace("https://github.com/", "").split("/");
        const owner = urlLimpia[0];
        const repo = urlLimpia[1];

        if (!owner || !repo) {
            throw new Error("La URL del repositorio no es válida. Debe ser estilo: https://github.com/usuario/repo");
        }

        // 2. Inicializar Octokit con el token seguro del usuario
        const octokit = new Octokit({ auth: token });

        console.log(`Conectando con GitHub para analizar: ${owner}/${repo}...`);

        // 3. Hacer la petición a la API de GitHub para obtener datos generales del repositorio
        const respuestaRepo = await octokit.request("GET /repos/{owner}/{repo}", {
            owner: owner,
            repo: repo,
            headers: {
                "X-GitHub-Api-Version": "2022-11-28"
            }
        });

        const datos = respuestaRepo.data;

        // 4. Estructurar las métricas clave que queremos devolver
        const metricas = {
            nombre: datos.name,
            descripcion: datos.description || "Sin descripción disponible.",
            estrellas: datos.stargazers_count,
            forks: datos.forks_count,
            issues_abiertos: datos.open_issues_count,
            licencia: datos.license ? datos.license.name : "No especificada",
            url_clonado: datos.clone_url,
            creado_el: datos.created_at,
            actualizado_el: datos.updated_at
        };

        return metricas;

    } catch (error) {
        console.error("Error al auditar el repositorio:", error.message);
        throw error;
    }
}
