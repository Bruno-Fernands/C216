import { useState } from "react";
import { paraApi, validarProduto } from "../validation.js";
import Campo from "./Campo.jsx";

const VAZIO = { nome: "", descricao: "", preco: "", estoque_minimo: "0" };

// Converte um produto da API para os campos (texto) do formulário.
function paraCampos(produto) {
  if (!produto) return VAZIO;
  return {
    nome: produto.nome,
    descricao: produto.descricao ?? "",
    preco: String(produto.preco).replace(".", ","),
    estoque_minimo: String(produto.estoque_minimo),
  };
}

// Serve para criar e para editar: com `produto`, o formulário vem preenchido.
// O App usa `key={produto?.id}` para recriá-lo ao trocar de produto.
export default function ProdutoForm({ produto, onSalvar, onCancelar }) {
  const [campos, setCampos] = useState(() => paraCampos(produto));
  const [erros, setErros] = useState({});
  const [enviando, setEnviando] = useState(false);
  const editando = Boolean(produto);

  const alterar = (nome) => (e) => setCampos((c) => ({ ...c, [nome]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    const novosErros = validarProduto(campos);
    setErros(novosErros);
    if (Object.keys(novosErros).length > 0) return;

    setEnviando(true);
    const salvou = await onSalvar(paraApi(campos));
    setEnviando(false);
    // Se a API recusar (ex.: nome repetido), mantém o que o usuário digitou.
    if (salvou && !editando) setCampos(VAZIO);
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-label={editando ? "Editar produto" : "Cadastrar produto"}
      className="space-y-4 rounded-xl bg-white p-4 shadow sm:p-6"
    >
      <h2 className="text-lg font-semibold text-slate-800">
        {editando ? `Editando: ${produto.nome}` : "Novo produto"}
      </h2>
      <Campo id="nome" rotulo="Nome" erro={erros.nome}>
        {(props) => <input {...props} value={campos.nome} onChange={alterar("nome")} />}
      </Campo>
      <Campo id="descricao" rotulo="Descrição (opcional)" erro={erros.descricao}>
        {(props) => (
          <textarea {...props} rows={2} value={campos.descricao} onChange={alterar("descricao")} />
        )}
      </Campo>
      <div className="grid gap-4 sm:grid-cols-2">
        <Campo id="preco" rotulo="Preço (R$)" erro={erros.preco}>
          {(props) => (
            <input
              {...props}
              inputMode="decimal"
              value={campos.preco}
              onChange={alterar("preco")}
            />
          )}
        </Campo>
        <Campo id="estoque_minimo" rotulo="Estoque mínimo" erro={erros.estoque_minimo}>
          {(props) => (
            <input
              {...props}
              inputMode="numeric"
              value={campos.estoque_minimo}
              onChange={alterar("estoque_minimo")}
            />
          )}
        </Campo>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        <button
          type="submit"
          disabled={enviando}
          className="rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
        >
          {enviando ? "Salvando..." : editando ? "Salvar alterações" : "Cadastrar"}
        </button>
        {editando && (
          <button
            type="button"
            onClick={onCancelar}
            className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancelar
          </button>
        )}
      </div>
    </form>
  );
}
