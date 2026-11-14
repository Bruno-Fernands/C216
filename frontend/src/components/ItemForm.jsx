import { useState } from "react";
import { validarItem } from "../validation.js";

const inputBase =
  "w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500";

export default function ItemForm({ onAdicionar }) {
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");
  const [erros, setErros] = useState({});

  function handleSubmit(e) {
    e.preventDefault();
    const novosErros = validarItem({ nome, descricao });
    setErros(novosErros);
    if (Object.keys(novosErros).length > 0) return;

    onAdicionar({ nome: nome.trim(), descricao: descricao.trim() });
    setNome("");
    setDescricao("");
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-label="Adicionar item"
      className="space-y-4 rounded-xl bg-white p-4 shadow sm:p-6"
    >
      <div>
        <label htmlFor="nome" className="mb-1 block text-sm font-medium text-slate-700">
          Nome
        </label>
        <input
          id="nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          aria-invalid={Boolean(erros.nome)}
          aria-describedby={erros.nome ? "nome-erro" : undefined}
          className={`${inputBase} ${erros.nome ? "border-red-500" : "border-slate-300"}`}
        />
        {erros.nome && (
          <p id="nome-erro" role="alert" className="mt-1 text-sm text-red-600">
            {erros.nome}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="descricao" className="mb-1 block text-sm font-medium text-slate-700">
          Descrição
        </label>
        <textarea
          id="descricao"
          rows={3}
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          aria-invalid={Boolean(erros.descricao)}
          aria-describedby={erros.descricao ? "descricao-erro" : undefined}
          className={`${inputBase} ${erros.descricao ? "border-red-500" : "border-slate-300"}`}
        />
        {erros.descricao && (
          <p id="descricao-erro" role="alert" className="mt-1 text-sm text-red-600">
            {erros.descricao}
          </p>
        )}
      </div>

      <button
        type="submit"
        className="w-full rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none sm:w-auto"
      >
        Adicionar
      </button>
    </form>
  );
}
