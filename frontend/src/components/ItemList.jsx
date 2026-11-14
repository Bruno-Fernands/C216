export default function ItemList({ itens }) {
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
        <li key={item.id} className="rounded-xl bg-white p-4 shadow">
          <h3 className="font-semibold break-words text-slate-800">{item.nome}</h3>
          <p className="text-sm break-words text-slate-600">{item.descricao}</p>
        </li>
      ))}
    </ul>
  );
}
