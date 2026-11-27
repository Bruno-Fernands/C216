import { useCallback, useEffect, useState } from "react";
import { listarMovimentacoes } from "../services/produtos.js";
import { validarMovimentacao } from "../validation.js";
import Campo from "./Campo.jsx";

const dataHora = (iso) =>
  new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });

// Formulário de entrada/saída + histórico do produto selecionado.
// `onRegistrar` devolve true quando a API aceitou a movimentação.
export default function MovimentacaoPanel({ produto, onRegistrar, onFechar }) {
  const [tipo, setTipo] = useState("entrada");
  const [quantidade, setQuantidade] = useState("");
  const [observacao, setObservacao] = useState("");
  const [erro, setErro] = useState("");
  const [historico, setHistorico] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erroHistorico, setErroHistorico] = useState("");

  const carregarHistorico = useCallback(async () => {
    try {
      setHistorico(await listarMovimentacoes(produto.id));
      setErroHistorico("");
    } catch (e) {
      setErroHistorico(e.message);
    } finally {
      setCarregando(false);
    }
  }, [produto.id]);

  // O App recria o painel (key) ao trocar de produto, então isto roda uma vez.
  useEffect(() => {
    carregarHistorico();
  }, [carregarHistorico]);

  async function handleSubmit(e) {
    e.preventDefault();
    const erros = validarMovimentacao({ quantidade });
    setErro(erros.quantidade ?? "");
    if (erros.quantidade) return;

    const salvou = await onRegistrar(produto, {
      tipo,
      quantidade: Number(quantidade),
      observacao: observacao.trim() || null,
    });
    if (salvou) {
      setQuantidade("");
      setObservacao("");
      await carregarHistorico();
    }
  }

  return (
    <section aria-label="Movimentações" className="space-y-4 rounded-xl bg-white p-4 shadow sm:p-6">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Movimentar: {produto.nome}</h2>
          <p className="text-sm text-slate-600">Saldo atual: {produto.quantidade}</p>
        </div>
        <button
          type="button"
          onClick={onFechar}
          aria-label="Fechar movimentações"
          className="rounded-md px-2 text-xl text-slate-500 hover:bg-slate-100"
        >
          ×
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        noValidate
        aria-label="Registrar movimentação"
        className="space-y-3"
      >
        <fieldset className="flex gap-4 text-sm">
          <legend className="sr-only">Tipo</legend>
          {[
            ["entrada", "Entrada"],
            ["saida", "Saída"],
          ].map(([valor, texto]) => (
            <label key={valor} className="flex items-center gap-1">
              <input
                type="radio"
                name="tipo"
                value={valor}
                checked={tipo === valor}
                onChange={() => setTipo(valor)}
              />
              {texto}
            </label>
          ))}
        </fieldset>
        <Campo id="quantidade" rotulo="Quantidade" erro={erro}>
          {(props) => (
            <input
              {...props}
              inputMode="numeric"
              value={quantidade}
              onChange={(e) => setQuantidade(e.target.value)}
            />
          )}
        </Campo>
        <Campo id="observacao" rotulo="Observação (opcional)">
          {(props) => (
            <input
              {...props}
              maxLength={200}
              value={observacao}
              onChange={(e) => setObservacao(e.target.value)}
            />
          )}
        </Campo>
        <button
          type="submit"
          className="rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none"
        >
          Registrar
        </button>
      </form>

      <div>
        <h3 className="mb-2 font-semibold text-slate-800">Histórico</h3>
        {carregando ? (
          <p className="text-sm text-slate-500">Carregando histórico...</p>
        ) : erroHistorico ? (
          <p className="text-sm text-red-600">{erroHistorico}</p>
        ) : historico.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhuma movimentação ainda.</p>
        ) : (
          <ul aria-label="Histórico" className="divide-y divide-slate-100 text-sm">
            {historico.map((m) => (
              <li key={m.id} className="flex flex-wrap justify-between gap-2 py-2">
                <span className={m.tipo === "entrada" ? "text-emerald-700" : "text-red-700"}>
                  {m.tipo === "entrada" ? "+" : "−"}
                  {m.quantidade} {m.tipo === "entrada" ? "entrada" : "saída"}
                </span>
                <span className="text-slate-500">{dataHora(m.criada_em)}</span>
                {m.observacao && (
                  <span className="w-full break-words text-slate-600">{m.observacao}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
