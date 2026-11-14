export default function ItemList({ itens, onRemover }) {
  if (itens.length === 0) {
    return (
      <p className="rounded-xl border-2 border-dashed border-slate-300 p-6 text-center text-slate-500">
        Nenhum item cadastrado.
      </p>
    );
  }

  return (
    <ul aria-label="Itens cadastrados" className="grid gap-3 sm:grid-cols-2">
      {itens.map((item) => (
        <li
          key={item.id}
          className="flex items-start justify-between gap-3 rounded-xl bg-white p-4 shadow"
        >
          <div className="min-w-0">
            <h3 className="font-semibold break-words text-slate-800">{item.nome}</h3>
            <p className="text-sm break-words text-slate-600">{item.descricao}</p>
          </div>
          <button
            type="button"
            onClick={() => onRemover(item.id)}
            aria-label={`Remover ${item.nome}`}
            className="shrink-0 rounded-lg px-2 py-1 text-sm text-red-600 hover:bg-red-50 focus:ring-2 focus:ring-red-500 focus:outline-none"
          >
            Remover
          </button>
        </li>
      ))}
    </ul>
  );
}
