// URL da API embutida no build pelo Vite (VITE_API_URL); padrão para dev local.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function requisitar(caminho, opcoes) {
  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  } catch {
    throw new Error("Não foi possível conectar ao servidor.");
  }

  const corpo = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    // Erros de negócio (ex.: 409) vêm com `detail` em texto; 422 vem como lista.
    const detalhe = typeof corpo?.detail === "string" ? corpo.detail : null;
    throw new Error(detalhe ?? `Erro ${resposta.status} ao falar com o servidor.`);
  }
  return corpo;
}

export function listItems() {
  return requisitar("/items/");
}

export function createItem({ nome, descricao }) {
  return requisitar("/items/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, descricao }),
  });
}
