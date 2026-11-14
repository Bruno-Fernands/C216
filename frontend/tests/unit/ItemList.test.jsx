import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ItemList from "../../src/components/ItemList.jsx";

describe("ItemList", () => {
  it("mostra o estado vazio", () => {
    render(<ItemList itens={[]} />);
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("lista nome e descrição de cada item", () => {
    const itens = [
      { id: 1, nome: "Lápis", descricao: "HB" },
      { id: 2, nome: "Borracha", descricao: "Branca" },
    ];
    render(<ItemList itens={itens} />);

    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("Borracha")).toBeInTheDocument();
    expect(screen.getByText("Branca")).toBeInTheDocument();
  });
});
