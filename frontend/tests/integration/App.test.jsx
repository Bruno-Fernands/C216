import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";

async function adicionar(nome, descricao) {
  await userEvent.type(screen.getByLabelText("Nome"), nome);
  await userEvent.type(screen.getByLabelText("Descrição"), descricao);
  await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));
}

describe("App (formulário + lista)", () => {
  beforeEach(() => {
    vi.spyOn(globalThis, "fetch");
  });
  afterEach(() => {
    // Critério de aceite: nenhuma chamada ao backend.
    expect(globalThis.fetch).not.toHaveBeenCalled();
    vi.restoreAllMocks();
  });

  it("começa vazio", () => {
    render(<App />);
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Itens (0)" })).toBeInTheDocument();
  });

  it("adiciona itens à lista e atualiza o contador", async () => {
    render(<App />);
    await adicionar("Caderno", "Capa azul");
    await adicionar("Mochila", "Preta");

    const lista = screen.getByRole("list", { name: "Itens cadastrados" });
    expect(within(lista).getAllByRole("listitem")).toHaveLength(2);
    expect(within(lista).getByText("Capa azul")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Itens (2)" })).toBeInTheDocument();
  });

  it("não adiciona item inválido", async () => {
    render(<App />);
    await adicionar("ab", "x");
    expect(screen.getByRole("alert")).toHaveTextContent(/pelo menos 3/);
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  });

  it("remove um item e volta ao estado vazio", async () => {
    render(<App />);
    await adicionar("Caderno", "Capa azul");
    await userEvent.click(screen.getByRole("button", { name: "Remover Caderno" }));
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  });
});
