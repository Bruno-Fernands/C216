import { formatarMoeda } from "../validation.js";

export default function ResumoCards({ resumo }) {
  if (!resumo) return null;
  const cards = [
    ["Produtos", resumo.total_produtos],
    ["Unidades em estoque", resumo.total_unidades],
    ["Valor em estoque", formatarMoeda(resumo.valor_total)],
    ["Abaixo do mínimo", resumo.abaixo_do_minimo],
  ];
  return (
    <dl aria-label="Resumo do estoque" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map(([rotulo, valor]) => (
        <div key={rotulo} className="rounded-xl bg-white p-4 shadow">
          <dt className="text-sm text-slate-500">{rotulo}</dt>
          <dd className="text-xl font-bold break-words text-slate-900">{valor}</dd>
        </div>
      ))}
    </dl>
  );
}
