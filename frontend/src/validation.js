// Mesmos limites do backend (app/schemas/produto.py).
export const NOME_MIN = 2;
export const NOME_MAX = 80;
export const DESCRICAO_MAX = 300;

const inteiroNaoNegativo = (v) => /^\d+$/.test(String(v).trim());

// Regras puras: recebem os campos (como texto do formulário) e devolvem
// { campo: mensagem } só para os inválidos.
export function validarProduto({ nome = "", descricao = "", preco = "", estoque_minimo = "" }) {
  const erros = {};
  const n = nome.trim();

  if (!n) erros.nome = "O nome é obrigatório.";
  else if (n.length < NOME_MIN) erros.nome = `O nome deve ter pelo menos ${NOME_MIN} caracteres.`;
  else if (n.length > NOME_MAX) erros.nome = `O nome deve ter no máximo ${NOME_MAX} caracteres.`;

  if (descricao.trim().length > DESCRICAO_MAX)
    erros.descricao = `A descrição deve ter no máximo ${DESCRICAO_MAX} caracteres.`;

  if (!/^\d+([.,]\d{1,2})?$/.test(String(preco).trim()))
    erros.preco = "Informe um preço válido (ex.: 12,50).";

  if (!inteiroNaoNegativo(estoque_minimo))
    erros.estoque_minimo = "O estoque mínimo deve ser um número inteiro (0 ou mais).";

  return erros;
}

// O saldo suficiente para a saída é conferido pela API (responde 409).
export function validarMovimentacao({ quantidade = "" }) {
  if (!inteiroNaoNegativo(quantidade) || Number(quantidade) === 0)
    return { quantidade: "A quantidade deve ser um número inteiro maior que zero." };
  return {};
}

// Converte os campos do formulário para o JSON esperado pela API.
export function paraApi({ nome, descricao, preco, estoque_minimo }) {
  return {
    nome: nome.trim(),
    descricao: descricao.trim() || null,
    preco: String(preco).trim().replace(",", "."),
    estoque_minimo: Number(estoque_minimo),
  };
}

export const formatarMoeda = (valor) =>
  Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
