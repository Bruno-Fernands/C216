import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";
import { resposta } from "../respostas.js";

const RESUMO = { total_produtos: 1, total_unidades: 3, valor_total: "7.50", abaixo_do_minimo: 1 };
const CANETA = {
  id: 1,
  nome: "Caneta",
  descricao: null,
  preco: "2.50",
  quantidade: 3,
  estoque_minimo: 5,
  abaixo_do_minimo: true,
  criado_em: "2026-11-26T10:00:00Z",
};

// API falsa: responde de acordo com "MÉTODO /caminho"; o que não estiver
// em `rotas` devolve a lista/resumo padrão.
function apiFalsa(rotas = {}, produtos = [CANETA]) {
  fetch.mockImplementation((url, opcoes = {}) => {
    const caminho = new URL(url).pathname + new URL(url).search;
    const chave = `${opcoes.method ?? "GET"} ${caminho}`;
    if (chave in rotas) return rotas[chave]();
    if (chave === "GET /produtos/resumo") return resposta(200, RESUMO);
    if (chave.startsWith("GET /produtos/1/movimentacoes")) return resposta(200, []);
    if (chave.startsWith("GET /produtos")) return resposta(200, produtos);
    throw new Error(`Rota não mockada: ${chave}`);
  });
}

const chamadas = (metodo) => fetch.mock.calls.filter(([, o]) => (o?.method ?? "GET") === metodo);

describe("App (API mockada)", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal(
      "confirm",
      vi.fn(() => true),
    );
  });
  afterEach(() => vi.unstubAllGlobals());

  it("mostra 'carregando' e depois a lista e o resumo", async () => {
    apiFalsa();
    render(<App />);

    expect(screen.getByRole("status")).toHaveTextContent("Carregando produtos...");
    expect(await screen.findByRole("listitem", { name: "Caneta" })).toBeInTheDocument();
    expect(screen.getByText("R$ 7,50")).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("mostra erro quando a API não responde", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível conectar");
  });

  it("cadastra um produto e mostra mensagem de sucesso", async () => {
    apiFalsa({ "POST /produtos": () => resposta(201, { ...CANETA, id: 2, nome: "Lápis" }) });
    render(<App />);
    await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.type(screen.getByLabelText("Nome"), "Lápis");
    await userEvent.type(screen.getByLabelText("Preço (R$)"), "1,20");
    await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));

    expect(await screen.findByText("Produto cadastrado.")).toBeInTheDocument();
    expect(JSON.parse(chamadas("POST")[0][1].body)).toMatchObject({ nome: "Lápis", preco: "1.20" });
  });

  it("edita um produto existente com PUT", async () => {
    apiFalsa({ "PUT /produtos/1": () => resposta(200, { ...CANETA, nome: "Caneta preta" }) });
    render(<App />);
    const item = await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.click(within(item).getByRole("button", { name: "Editar" }));
    const nome = screen.getByLabelText("Nome");
    await userEvent.clear(nome);
    await userEvent.type(nome, "Caneta preta");
    await userEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));

    expect(await screen.findByText("Produto atualizado.")).toBeInTheDocument();
    expect(JSON.parse(chamadas("PUT")[0][1].body).nome).toBe("Caneta preta");
    expect(screen.getByRole("button", { name: "Cadastrar" })).toBeInTheDocument();
  });

  it("exclui após confirmação", async () => {
    apiFalsa({ "DELETE /produtos/1": () => resposta(204, null) });
    render(<App />);
    const item = await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.click(within(item).getByRole("button", { name: "Excluir" }));

    expect(confirm).toHaveBeenCalled();
    expect(await screen.findByText("Produto excluído.")).toBeInTheDocument();
  });

  it("não exclui se o usuário cancelar a confirmação", async () => {
    confirm.mockReturnValue(false);
    apiFalsa();
    render(<App />);
    const item = await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.click(within(item).getByRole("button", { name: "Excluir" }));
    expect(chamadas("DELETE")).toHaveLength(0);
  });

  it("mostra o erro da API quando a saída excede o saldo", async () => {
    apiFalsa({
      "POST /produtos/1/movimentacoes": () =>
        resposta(409, { detail: "Estoque insuficiente: disponível 3, solicitado 9." }),
    });
    render(<App />);
    const item = await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.click(within(item).getByRole("button", { name: "Movimentar" }));
    const painel = screen.getByRole("region", { name: "Movimentações" });
    await userEvent.click(within(painel).getByLabelText("Saída"));
    await userEvent.type(within(painel).getByLabelText("Quantidade"), "9");
    await userEvent.click(within(painel).getByRole("button", { name: "Registrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Estoque insuficiente");
    expect(within(painel).getByText("Saldo atual: 3")).toBeInTheDocument();
  });

  it("registra uma entrada e atualiza o saldo do painel", async () => {
    apiFalsa({
      "POST /produtos/1/movimentacoes": () =>
        resposta(201, { id: 1, produto_id: 1, tipo: "entrada", quantidade: 4 }),
    });
    render(<App />);
    const item = await screen.findByRole("listitem", { name: "Caneta" });

    await userEvent.click(within(item).getByRole("button", { name: "Movimentar" }));
    const painel = screen.getByRole("region", { name: "Movimentações" });
    await userEvent.type(within(painel).getByLabelText("Quantidade"), "4");
    await userEvent.click(within(painel).getByRole("button", { name: "Registrar" }));

    expect(await screen.findByText("Entrada registrada.")).toBeInTheDocument();
    expect(within(painel).getByText("Saldo atual: 7")).toBeInTheDocument();
  });
});
