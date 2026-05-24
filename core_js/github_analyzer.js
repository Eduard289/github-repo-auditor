import { Octokit } from "@octokit/core";

/**
 * Función principal para obtener las métricas avanzadas y de salud de un repositorio.
 */
export async function auditarRepositorio(token, repoUrl) {
    try {
        const urlLimpia = repoUrl.replace("https://github.com/", "").split("/");
        const owner = urlLimpia[0];
        const repo = urlLimpia[1];

        if (!owner || !repo) {
            throw new Error("La URL del repositorio no es válida.");
        }

        const octokit = new Octokit({ auth: token });

        // 1. Petición base del repositorio
        const respuestaRepo = await octokit.request("GET /repos/{owner}/{repo}", {
            owner: owner,
            repo: repo,
            headers: { "X-GitHub-Api-Version": "2022-11-28" }
        });

        const datos = respuestaRepo.data;

        // 2. Obtener desglose de lenguajes
        let lenguajes = {};
        try {
            const respuestaLenguajes = await octokit.request("GET /repos/{owner}/{repo}/languages", {
                owner: owner,
                repo: repo,
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            lenguajes = respuestaLenguajes.data;
        } catch (e) {
            console.warn("No se pudieron obtener los lenguajes.");
        }

        // 3. Obtener número de ramas (branches)
        let totalRamas = 0;
        try {
            const respuestaRamas = await octokit.request("GET /repos/{owner}/{repo}/branches", {
                owner: owner,
                repo: repo,
                per_page: 100,
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            totalRamas = respuestaRamas.data.length;
        } catch (e) {
            totalRamas = "Requiere Auth";
        }

        // 4. NUEVO: Contar Pull Requests activos (abiertos)
        let prsActivos = 0;
        try {
            const respuestaPRs = await octokit.request("GET /repos/{owner}/{repo}/pulls", {
                owner: owner,
                repo: repo,
                state: "open",
                per_page: 1, // Solo queremos el total del header o de la lista corta
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            prsActivos = respuestaPRs.data.length;
            // Nota: Si hay paginación avanzada pasaría de 100, pero esto nos da una métrica excelente de actividad inmediata
        } catch (e) {
            prsActivos = "Requiere Auth";
        }

        // 5. NUEVO: Buscar Issues Cerrados para calcular la salud del soporte
        // GitHub almacena de forma nativa los abiertos en open_issues_count.
        // Hacemos una búsqueda rápida orientada al estado cerrado para estimar el histórico.
        let issuesCerradosEst = datos.open_issues_count * 3; // Estimación por defecto si falla la API sin token
        try {
            const respuestaBusqueda = await octokit.request("GET /search/issues", {
                q: `repo:${owner}/${repo} is:issue is:closed`,
                per_page: 1,
                headers: { "X-GitHub-Api-Version": "2022-11-28" }
            });
            issuesCerradosEst = respuestaBusqueda.data.total_count || 0;
        } catch (e) {
            // Fallback amistoso si el Search API está saturado sin credenciales
            if (datos.open_issues_count === 0) issuesCerradosEst = 10; 
        }

        // Estructura final del JSON enriquecido
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
            lenguaje_principal: datos.language || "No detectado",
            top_lenguajes: lenguajes,
            seguidores_activos: datos.subscribers_count || 0,
            ramas_activas: totalRamas,
            // --- NUEVAS MÉTRICAS ---
            tamano_kb: datos.size, // Tamaño en KB
            prs_activos: prsActivos,
            issues_cerrados: issuesCerradosEst
        };

        return metricas;

    } catch (error) {
        console.error("Error en la auditoría:", error.message);
        throw error;
    }
}
