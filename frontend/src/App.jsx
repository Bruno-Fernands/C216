import { useEffect, useState } from "react";
import ItemForm from "./components/ItemForm.jsx";
import ItemList from "./components/ItemList.jsx";
import { createItem, listItems } from "./services/items.js";

export default function App() {
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true; // evita setState depois de desmontar
    listItems()
      .then((dados) => ativo && setItens(dados))
      .catch((e) => ativo && setErro(e.message))
      .finally(() => ativo && setCarregando(false));
    return () => {
      ativo = false;
    };
  }, []);

  // Devolve true quando salvou, para o formulário saber se deve limpar os campos.
  async function adicionar(item) {
    setErro("");
    try {
      const criado = await createItem(item);
      setItens((atuais) => [...atuais, criado]);
      return true;
    } catch (e) {
      setErro(e.message);
      return false;
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto max-w-3xl space-y-6">
        <header>
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Gerenciador de Itens</h1>
          <p className="text-slate-600">Cadastre itens com nome e descrição.</p>
        </header>
        {erro && (
          <div
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {erro}
          </div>
        )}
        <ItemForm onAdicionar={adicionar} />
        <section aria-labelledby="titulo-lista" aria-busy={carregando} className="space-y-3">
          <h2 id="titulo-lista" className="text-lg font-semibold text-slate-800">
            Itens ({itens.length})
          </h2>
          {carregando ? (
            <p role="status" className="text-slate-500">
              Carregando itens...
            </p>
          ) : (
            <ItemList itens={itens} />
          )}
        </section>
      </div>
    </main>
  );
}
