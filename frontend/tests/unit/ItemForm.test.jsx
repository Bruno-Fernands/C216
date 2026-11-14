import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ItemForm from "../../src/components/ItemForm.jsx";

async function preencherEEnviar(nome, descricao) {
  await userEvent.type(screen.getByLabelText("Nome"), nome);
  await userEvent.type(screen.getByLabelText("Descrição"), descricao);
  await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));
}

describe("ItemForm", () => {
  it("mostra erros e não envia quando inválido", async () => {
    const onAdicionar = vi.fn();
    render(<ItemForm onAdicionar={onAdicionar} />);

    await userEvent.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(screen.getAllByRole("alert")).toHaveLength(2);
    expect(screen.getByLabelText("Nome")).toHaveAttribute("aria-invalid", "true");
    expect(onAdicionar).not.toHaveBeenCalled();
  });

  it("envia sem espaços extras e limpa os campos quando salvou", async () => {
    const onAdicionar = vi.fn().mockResolvedValue(true);
    render(<ItemForm onAdicionar={onAdicionar} />);

    await preencherEEnviar("  Caneta  ", "Tinta preta");

    expect(onAdicionar).toHaveBeenCalledWith({ nome: "Caneta", descricao: "Tinta preta" });
    expect(screen.getByLabelText("Nome")).toHaveValue("");
    expect(screen.getByLabelText("Descrição")).toHaveValue("");
  });

  it("mantém os campos quando a API recusa", async () => {
    render(<ItemForm onAdicionar={vi.fn().mockResolvedValue(false)} />);

    await preencherEEnviar("Caneta", "Tinta preta");

    expect(screen.getByLabelText("Nome")).toHaveValue("Caneta");
  });

  it("desabilita o botão enquanto salva", async () => {
    let concluir;
    const onAdicionar = vi.fn(() => new Promise((r) => (concluir = r)));
    render(<ItemForm onAdicionar={onAdicionar} />);

    await preencherEEnviar("Caneta", "Tinta preta");
    expect(screen.getByRole("button", { name: "Salvando..." })).toBeDisabled();

    concluir(true);
    expect(await screen.findByRole("button", { name: "Adicionar" })).toBeEnabled();
  });
});
