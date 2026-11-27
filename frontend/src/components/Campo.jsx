// Rótulo + controle + mensagem de erro acessível, usado pelos formulários.
export const inputBase =
  "w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500";

export default function Campo({ id, rotulo, erro, children }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-slate-700">
        {rotulo}
      </label>
      {children({
        id,
        "aria-invalid": Boolean(erro),
        "aria-describedby": erro ? `${id}-erro` : undefined,
        className: `${inputBase} ${erro ? "border-red-500" : "border-slate-300"}`,
      })}
      {erro && (
        <p id={`${id}-erro`} role="alert" className="mt-1 text-sm text-red-600">
          {erro}
        </p>
      )}
    </div>
  );
}
