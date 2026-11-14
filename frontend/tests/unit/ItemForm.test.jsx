import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ItemForm from "../../src/components/ItemForm.jsx";

describe("ItemForm", () => {
  it("mostra erros e não envia quando inválido", async () => {
    const onAdicionar = vi.fn();
    render(<ItemForm onAdicionar={onAdicionar} />);

    await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(screen.getAllByRole("alert")).toHaveLength(2);
    expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "true");
    expect(onAdicionar).not.toHaveBeenCalled();
  });

  it("envia os dados sem espaços extras e limpa os campos", async () => {
    const onAdicionar = vi.fn();
    render(<ItemForm onAdicionar={onAdicionar} />);

    await userEvent.type(screen.getByLabelText("Nome"), "  Caneta  ");
    await userEvent.type(screen.getByLabelText("Descrição"), "Tinta preta");
    await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(onAdicionar).toHaveBeenCalledWith({ nome: "Caneta", descricao: "Tinta preta" });
    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(screen.getByLabelText("Descrição")).toHaveValue("");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
