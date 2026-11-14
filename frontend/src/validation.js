export const NOME_MIN = 3;
export const NOME_MAX = 50;
export const DESCRICAO_MAX = 200;

// Regra pura: recebe os campos e devolve { campo: mensagem } só para os inválidos.
export function validarItem({ nome = "", descricao = "" }) {
  const erros = {};
  const n = nome.trim();
  const d = descricao.trim();

  if (!n) erros.nome = "O nome é obrigatório.";
  else if (n.length < NOME_MIN) erros.nome = `O nome deve ter pelo menos ${NOME_MIN} caracteres.`;
  else if (n.length > NOME_MAX) erros.nome = `O nome deve ter no máximo ${NOME_MAX} caracteres.`;

  if (!d) erros.descricao = "A descrição é obrigatória.";
  else if (d.length > DESCRICAO_MAX)
    erros.descricao = `A descrição deve ter no máximo ${DESCRICAO_MAX} caracteres.`;

  return erros;
}
