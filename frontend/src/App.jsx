import { useCallback, useEffect, useState } from "react";
import MovimentacaoPanel from "./components/MovimentacaoPanel.jsx";
import ProdutoForm from "./components/ProdutoForm.jsx";
import ProdutoList from "./components/ProdutoList.jsx";
import ResumoCards from "./components/ResumoCards.jsx";
import {
  atualizarProduto,
  criarProduto,
  listarProdutos,
  obterResumo,
  registrarMovimentacao,
  removerProduto,
} from "./services/produtos.js";

export default function App() {
  const [produtos, setProdutos] = useState([]);
  const [resumo, setResumo] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");
  const [busca, setBusca] = useState("");
  const [abaixoDoMinimo, setAbaixoDoMinimo] = useState(false);
  const [editando, setEditando] = useState(null);
  const [movimentando, setMovimentando] = useState(null);

  // Lista e resumo vêm sempre da API, assim a tela reflete o banco.
  const recarregar = useCallback(async () => {
    const [lista, totais] = await Promise.all([
      listarProdutos({ busca, abaixoDoMinimo }),
      obterResumo(),
    ]);
    setProdutos(lista);
    setResumo(totais);
  }, [busca, abaixoDoMinimo]);

  useEffect(() => {
    let ativo = true;
    // Espera o usuário parar de digitar antes de buscar.
    const timer = setTimeout(() => {
      recarregar()
        .then(() => ativo && setErro(""))
        .catch((e) => ativo && setErro(e.message))
        .finally(() => ativo && setCarregando(false));
    }, 250);
    return () => {
      ativo = false;
      clearTimeout(timer);
    };
  }, [recarregar]);

  // Executa uma ação na API, mostra o resultado e devolve true se deu certo.
  async function executar(acao, mensagem) {
    setErro("");
    setSucesso("");
    let resultado;
    try {
      resultado = await acao();
    } catch (e) {
      setErro(e.message);
      return false;
    }
    setSucesso(mensagem);
    // A ação já foi gravada: uma falha ao recarregar não a desfaz.
    await recarregar().catch((e) => setErro(e.message));
    return resultado ?? true;
  }

  async function salvar(dados) {
    if (!editando) return executar(() => criarProduto(dados), "Produto cadastrado.");
    const atualizado = await executar(
      () => atualizarProduto(editando.id, dados),
      "Produto atualizado.",
    );
    if (atualizado) {
      setEditando(null);
      if (movimentando?.id === atualizado.id) setMovimentando(atualizado);
    }
    return Boolean(atualizado);
  }

  async function excluir(produto) {
    if (!window.confirm(`Excluir "${produto.nome}" e todo o seu histórico?`)) return;
    const ok = await executar(() => removerProduto(produto.id), "Produto excluído.");
    if (ok) {
      if (editando?.id === produto.id) setEditando(null);
      if (movimentando?.id === produto.id) setMovimentando(null);
    }
  }

  async function movimentar(produto, dados) {
    const ok = await executar(
      () => registrarMovimentacao(produto.id, dados),
      dados.tipo === "entrada" ? "Entrada registrada." : "Saída registrada.",
    );
    if (ok) {
      const delta = dados.tipo === "entrada" ? dados.quantidade : -dados.quantidade;
      setMovimentando({ ...produto, quantidade: produto.quantidade + delta });
    }
    return Boolean(ok);
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header>
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Controle de Estoque</h1>
          <p className="text-slate-600">
            Cadastre produtos e registre entradas e saídas. O saldo só muda por movimentações.
          </p>
        </header>

        <ResumoCards resumo={resumo} />

        {erro && (
          <div
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {erro}
          </div>
        )}
        <div aria-live="polite">
          {sucesso && (
            <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              {sucesso}
            </p>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.3fr)]">
          <div className="space-y-6">
            <ProdutoForm
              key={editando?.id ?? "novo"}
              produto={editando}
              onSalvar={salvar}
              onCancelar={() => setEditando(null)}
            />
            {movimentando && (
              <MovimentacaoPanel
                key={movimentando.id}
                produto={movimentando}
                onRegistrar={movimentar}
                onFechar={() => setMovimentando(null)}
              />
            )}
          </div>

          <section aria-labelledby="titulo-lista" aria-busy={carregando} className="space-y-3">
            <h2 id="titulo-lista" className="text-lg font-semibold text-slate-800">
              Produtos ({produtos.length})
            </h2>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <input
                type="search"
                aria-label="Buscar por nome"
                placeholder="Buscar por nome..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500 sm:flex-1"
              />
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={abaixoDoMinimo}
                  onChange={(e) => setAbaixoDoMinimo(e.target.checked)}
                />
                Só estoque baixo
              </label>
            </div>
            {carregando ? (
              <p role="status" className="text-slate-500">
                Carregando produtos...
              </p>
            ) : (
              <ProdutoList
                produtos={produtos}
                selecionadoId={movimentando?.id}
                onEditar={setEditando}
                onExcluir={excluir}
                onMovimentar={setMovimentando}
              />
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
