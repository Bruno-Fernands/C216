import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ItemList from "../../src/components/ItemList.jsx";

describe("ItemList", () => {
  it("mostra o estado vazio", () => {
    render(<ItemList itens={[]} onRemover={() => {}} />);
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("lista os itens e chama onRemover com o id", async () => {
    const onRemover = vi.fn();
    const itens = [
      { id: "1", nome: "Lápis", descricao: "HB" },
      { id: "2", nome: "Borracha", descricao: "Branca" },
    ];
    render(<ItemList itens={itens} onRemover={onRemover} />);

    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    await userEvent.click(screen.getByRole("button", { name: "Remover Borracha" }));
    expect(onRemover).toHaveBeenCalledWith("2");
  });
});
