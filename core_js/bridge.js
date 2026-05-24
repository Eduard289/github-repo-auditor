import { auditarRepositorio } from "./github_analyzer.js";

async function ejecutar() {
    // Recogemos el token y la URL del repositorio que nos pasa Python por la terminal
    const token = process.argv[2];
    const repoUrl = process.argv[3];

    if (!repoUrl) {
        console.error(JSON.stringify({ error: "No se ha proporcionado la URL del repositorio." }));
        process.exit(1);
    }

    try {
        // Ejecutamos la auditoría pasando null si el token es la cadena "null"
        const resultado = await auditarRepositorio(token === "null" ? null : token, repoUrl);
        
        // Imprimimos el resultado final en formato JSON en la consola para que Python lo lea
        console.log(JSON.stringify(resultado));
    } catch (error) {
        console.error(JSON.stringify({ error: error.message }));
        process.exit(1);
    }
}

ejecutar();
