// URL da API embutida no build pelo Vite (VITE_API_URL); padrão para dev local.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const JSON_HEADERS = { "Content-Type": "application/json" };

async function requisitar(caminho, opcoes) {
  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes);
  } catch {
    throw new Error("Não foi possível conectar ao servidor.");
  }

  // 204 (DELETE) não tem corpo.
  const corpo = resposta.status === 204 ? null : await resposta.json().catch(() => null);
  if (!resposta.ok) {
    // Erros de negócio (404/409) vêm com `detail` em texto; 422 vem como lista.
    const detalhe = typeof corpo?.detail === "string" ? corpo.detail : null;
    throw new Error(detalhe ?? `Erro ${resposta.status} ao falar com o servidor.`);
  }
  return corpo;
}

function enviar(metodo, caminho, dados) {
  return requisitar(caminho, {
    method: metodo,
    headers: JSON_HEADERS,
    body: JSON.stringify(dados),
  });
}

export function listarProdutos({ busca = "", abaixoDoMinimo = false } = {}) {
  const params = new URLSearchParams();
  if (busca.trim()) params.set("busca", busca.trim());
  if (abaixoDoMinimo) params.set("abaixo_do_minimo", "true");
  const query = params.toString();
  return requisitar(`/produtos${query ? `?${query}` : ""}`);
}

export const obterResumo = () => requisitar("/produtos/resumo");
export const criarProduto = (dados) => enviar("POST", "/produtos", dados);
export const atualizarProduto = (id, dados) => enviar("PUT", `/produtos/${id}`, dados);
export const removerProduto = (id) => requisitar(`/produtos/${id}`, { method: "DELETE" });
export const listarMovimentacoes = (id) => requisitar(`/produtos/${id}/movimentacoes`);
export const registrarMovimentacao = (id, dados) =>
  enviar("POST", `/produtos/${id}/movimentacoes`, dados);
