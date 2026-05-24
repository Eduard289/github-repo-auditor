import { Octokit } from "@octokit/core";

/**
 * Función principal para obtener las métricas avanzadas de un repositorio.
 * @param {string} token - El Personal Access Token de GitHub del usuario.
 * @param {string} repoUrl - La URL completa del repositorio.
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

        // 3. Hacer la petición a la API de GitHub para obtener datos generales del repositorio
        const respuestaRepo = await octokit.request("GET /repos/{owner}/{repo}", {
            owner: owner,
            repo: repo,
            headers: { "X-GitHub-Api-Version": "2022-11-28" }
        });

        const datos = respuestaRepo.data;

        // 4. Petición extra: Obtener el desglose de lenguajes del repositorio
        let lenguajes = {};
        try {
            const respuestaLenguajes = await octokit.request("GET /repos/{owner}/{repo}/languages", {
                owner: owner,
                repo: repo,
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            lenguajes = respuestaLenguajes.data;
        } catch (e) {
            console.warn("No se pudieron obtener los lenguajes detallados.");
        }

        // 5. Petición extra: Intentar obtener las ramas (branches) del repositorio
        let totalRamas = 0;
        try {
            const respuestaRamas = await octokit.request("GET /repos/{owner}/{repo}/branches", {
                owner: owner,
                repo: repo,
                per_page: 100, // Máximo por página estándar
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            totalRamas = respuestaRamas.data.length;
        } catch (e) {
            totalRamas = "Requiere Auth/Admin";
        }

        // 6. Estructurar el nuevo JSON con los tres nuevos parámetros incluidos
        const metricas = {
            nombre: datos.name,
            descripcion: datos.description || "Sin descripción disponible.",
            estrellas: datos.stargazers_count,
            forks: datos.forks_count,
            issues_abiertos: datos.open_issues_count,
            licencia: datos.license ? datos.license.name : "No especificada",
            url_clonado: datos.clone_url,
            creado_el: datos.created_at,
            actualizado_el: datos.updated_at,
            // --- NUEVOS PARÁMETROS ---
            lenguaje_principal: datos.language || "No detectado",
            top_lenguajes: lenguajes,
            seguidores_activos: datos.subscribers_count || 0,
            ramas_activas: totalRamas
        };

        return metricas;

    } catch (error) {
        console.error("Error al auditar el repositorio:", error.message);
        throw error;
    }
}
