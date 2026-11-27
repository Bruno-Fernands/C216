import { formatarMoeda } from "../validation.js";

const botao = "rounded-md px-3 py-1 text-sm font-medium focus:ring-2 focus:outline-none";

export default function ProdutoList({
  produtos,
  selecionadoId,
  onEditar,
  onExcluir,
  onMovimentar,
}) {
  if (produtos.length === 0) {
    return (
      <p className="rounded-xl border-2 border-dashed border-slate-300 p-6 text-center text-slate-500">
        Nenhum produto encontrado.
      </p>
    );
  }

  return (
    <ul aria-label="Produtos" className="space-y-3">
      {produtos.map((p) => (
        <li
          key={p.id}
          aria-label={p.nome}
          className={`rounded-xl bg-white p-4 shadow ${p.id === selecionadoId ? "ring-2 ring-indigo-500" : ""}`}
        >
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="font-semibold break-words text-slate-800">{p.nome}</h3>
              {p.descricao && <p className="text-sm break-words text-slate-600">{p.descricao}</p>}
            </div>
            {p.abaixo_do_minimo && (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                Estoque baixo
              </span>
            )}
          </div>
          <dl className="mt-2 grid grid-cols-3 gap-2 text-sm">
            <div>
              <dt className="text-slate-500">Saldo</dt>
              <dd className="font-semibold text-slate-800">{p.quantidade}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Mínimo</dt>
              <dd className="text-slate-800">{p.estoque_minimo}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Preço</dt>
              <dd className="text-slate-800">{formatarMoeda(p.preco)}</dd>
            </div>
          </dl>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => onMovimentar(p)}
              className={`${botao} bg-indigo-50 text-indigo-700 hover:bg-indigo-100 focus:ring-indigo-500`}
            >
              Movimentar
            </button>
            <button
              type="button"
              onClick={() => onEditar(p)}
              className={`${botao} bg-slate-100 text-slate-700 hover:bg-slate-200 focus:ring-slate-400`}
            >
              Editar
            </button>
            <button
              type="button"
              onClick={() => onExcluir(p)}
              className={`${botao} bg-red-50 text-red-700 hover:bg-red-100 focus:ring-red-500`}
            >
              Excluir
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
