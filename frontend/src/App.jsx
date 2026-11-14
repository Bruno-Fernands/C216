import { useState } from "react";
import ItemForm from "./components/ItemForm.jsx";
import ItemList from "./components/ItemList.jsx";

export default function App() {
  // Estado só em memória: a prática pede nenhuma chamada ao backend.
  const [itens, setItens] = useState([]);

  function adicionar(item) {
    setItens((atuais) => [...atuais, { id: crypto.randomUUID(), ...item }]);
  }

  function remover(id) {
    setItens((atuais) => atuais.filter((item) => item.id !== id));
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <header>
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Gerenciador de Itens</h1>
          <p className="text-slate-600">Cadastre itens com nome e descrição.</p>
        </header>
        <ItemForm onAdicionar={adicionar} />
        <section aria-labelledby="titulo-lista" className="space-y-3">
          <h2 id="titulo-lista" className="text-lg font-semibold text-slate-800">
            Itens ({itens.length})
          </h2>
          <ItemList itens={itens} onRemover={remover} />
        </section>
      </div>
    </main>
  );
}
