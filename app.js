// app.js

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

// --- FUNÇÃO PARA TESTAR A CONEXÃO COM A API ---
async function testAPIConnection() {
    console.log("Tentando conectar à API em:", API_BASE_URL);
    try {
        const response = await fetch(API_BASE_URL); // Faz uma chamada para o endpoint raiz "/"
        
        if (!response.ok) {
            throw new Error(`O servidor respondeu com o status: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log("✅ Conexão com a API bem-sucedida!");
        console.log("Resposta do servidor:", data);
        alert("Sucesso! O frontend está conectado ao backend. Verifique o console para mais detalhes.");

    } catch (error) {
        console.error("❌ Falha na conexão com a API:", error);
        alert(`Erro ao conectar com o backend. Verifique se a URL da API está correta e se o servidor está no ar. Detalhes do erro no console.`);
    }
}

// --- INICIALIZAÇÃO ---
// Quando a página terminar de carregar, executa o teste de conexão.
document.addEventListener('DOMContentLoaded', () => {
    testAPIConnection();
});