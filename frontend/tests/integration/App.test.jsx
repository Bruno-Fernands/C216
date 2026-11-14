import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";
import { resposta } from "../respostas.js";

async function adicionar(nome, descricao) {
  await userEvent.type(screen.getByLabelText("Nome"), nome);
  await userEvent.type(screen.getByLabelText("Descrição"), descricao);
  await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));
}

describe("App (formulário + lista + API mockada)", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it("mostra 'carregando' enquanto a lista não chega", async () => {
    let entregar;
    fetch.mockReturnValue(new Promise((r) => (entregar = r)));
    render(<App />);

    expect(screen.getByRole("status")).toHaveTextContent("Carregando itens...");

    entregar(await resposta(200, []));
    expect(await screen.findByText("Nenhum item cadastrado.")).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("exibe os itens vindos da API", async () => {
    fetch.mockReturnValue(
      resposta(200, [
        { id: 1, nome: "Caderno", descricao: "Capa azul" },
        { id: 2, nome: "Mochila", descricao: "Preta" },
      ]),
    );
    render(<App />);

    const lista = await screen.findByRole("list", { name: "Itens cadastrados" });
    expect(within(lista).getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByRole("heading", { name: "Itens (2)" })).toBeInTheDocument();
  });

  it("mostra erro quando a API não responde", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));
    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível conectar");
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  });

  it("cria um item pela API e o adiciona à lista", async () => {
    fetch
      .mockReturnValueOnce(resposta(200, []))
      .mockReturnValueOnce(resposta(201, { id: 7, nome: "Caderno", descricao: "Capa azul" }));
    render(<App />);
    await screen.findByText("Nenhum item cadastrado.");

    await adicionar("Caderno", "Capa azul");

    expect(await screen.findByText("Capa azul")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Itens (1)" })).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith(
      "http://localhost:8000/items/",
      expect.objectContaining({ method: "POST" }),
    );
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("mostra a mensagem da API para nome repetido e não altera a lista", async () => {
    fetch
      .mockReturnValueOnce(resposta(200, [{ id: 1, nome: "Caderno", descricao: "A" }]))
      .mockReturnValueOnce(resposta(409, { detail: "Já existe um item com esse nome" }));
    render(<App />);
    await screen.findByRole("list");

    await adicionar("Caderno", "B");

    expect(await screen.findByRole("alert")).toHaveTextContent("Já existe um item com esse nome");
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
    expect(screen.getByLabelText("Nome")).toHaveValue("Caderno");
  });

  it("não chama a API quando o formulário é inválido", async () => {
    fetch.mockReturnValue(resposta(200, []));
    render(<App />);
    await screen.findByText("Nenhum item cadastrado.");

    await adicionar("ab", "x");

    expect(screen.getByRole("alert")).toHaveTextContent(/pelo menos 3/);
    expect(fetch).toHaveBeenCalledTimes(1); // só o GET inicial
  });
});
