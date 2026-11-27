import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ProdutoForm from "../../src/components/ProdutoForm.jsx";
import ProdutoList from "../../src/components/ProdutoList.jsx";
import ResumoCards from "../../src/components/ResumoCards.jsx";

const PRODUTO = {
  id: 1,
  nome: "Caneta",
  descricao: "Azul",
  preco: "2.50",
  quantidade: 3,
  estoque_minimo: 5,
  abaixo_do_minimo: true,
};

describe("ProdutoForm", () => {
  it("valida antes de enviar", async () => {
    const onSalvar = vi.fn();
    render(<ProdutoForm onSalvar={onSalvar} />);

    await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));

    expect(screen.getByText("O nome é obrigatório.")).toBeInTheDocument();
    expect(screen.getByText(/preço válido/)).toBeInTheDocument();
    expect(onSalvar).not.toHaveBeenCalled();
  });

  it("envia os dados convertidos e limpa ao salvar", async () => {
    const onSalvar = vi.fn().mockResolvedValue(true);
    render(<ProdutoForm onSalvar={onSalvar} />);

    await userEvent.type(screen.getByLabelText("Nome"), "Caneta");
    await userEvent.type(screen.getByLabelText("Preço (R$)"), "2,5");
    await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));

    expect(onSalvar).toHaveBeenCalledWith({
      nome: "Caneta",
      descricao: null,
      preco: "2.5",
      estoque_minimo: 0,
    });
    expect(screen.getByLabelText("Nome")).toHaveValue("");
  });

  it("no modo edição vem preenchido e permite cancelar", async () => {
    const onCancelar = vi.fn();
    render(<ProdutoForm produto={PRODUTO} onSalvar={vi.fn()} onCancelar={onCancelar} />);

    expect(screen.getByLabelText("Nome")).toHaveValue("Caneta");
    expect(screen.getByLabelText("Preço (R$)")).toHaveValue("2,50");
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(onCancelar).toHaveBeenCalled();
  });
});

describe("ProdutoList", () => {
  it("mostra saldo, alerta de estoque baixo e dispara as ações", async () => {
    const acoes = { onEditar: vi.fn(), onExcluir: vi.fn(), onMovimentar: vi.fn() };
    render(<ProdutoList produtos={[PRODUTO]} {...acoes} />);

    const item = screen.getByRole("listitem", { name: "Caneta" });
    expect(within(item).getByText("Estoque baixo")).toBeInTheDocument();
    expect(within(item).getByText("R$ 2,50")).toBeInTheDocument();

    await userEvent.click(within(item).getByRole("button", { name: "Editar" }));
    await userEvent.click(within(item).getByRole("button", { name: "Excluir" }));
    await userEvent.click(within(item).getByRole("button", { name: "Movimentar" }));
    expect(acoes.onEditar).toHaveBeenCalledWith(PRODUTO);
    expect(acoes.onExcluir).toHaveBeenCalledWith(PRODUTO);
    expect(acoes.onMovimentar).toHaveBeenCalledWith(PRODUTO);
  });

  it("mostra mensagem quando não há produtos", () => {
    render(<ProdutoList produtos={[]} />);
    expect(screen.getByText("Nenhum produto encontrado.")).toBeInTheDocument();
  });
});

describe("ResumoCards", () => {
  it("formata os totais", () => {
    render(
      <ResumoCards
        resumo={{ total_produtos: 2, total_unidades: 7, valor_total: "40.00", abaixo_do_minimo: 1 }}
      />,
    );
    expect(screen.getByText("R$ 40,00")).toBeInTheDocument();
    expect(screen.getByText("Unidades em estoque").nextSibling).toHaveTextContent("7");
  });
});
