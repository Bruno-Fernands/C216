import { describe, expect, it } from "vitest";
import { paraApi, validarMovimentacao, validarProduto } from "../../src/validation.js";

const VALIDO = { nome: "Caneta", descricao: "", preco: "2,50", estoque_minimo: "5" };

describe("validarProduto", () => {
  it("aceita um produto válido", () => {
    expect(validarProduto(VALIDO)).toEqual({});
  });

  it.each([
    [{ nome: "" }, "nome", "obrigatório"],
    [{ nome: " a " }, "nome", "pelo menos 2"],
    [{ nome: "x".repeat(81) }, "nome", "no máximo 80"],
    [{ descricao: "x".repeat(301) }, "descricao", "no máximo 300"],
    [{ preco: "" }, "preco", "preço válido"],
    [{ preco: "-1" }, "preco", "preço válido"],
    [{ preco: "1,999" }, "preco", "preço válido"],
    [{ estoque_minimo: "1.5" }, "estoque_minimo", "inteiro"],
    [{ estoque_minimo: "" }, "estoque_minimo", "inteiro"],
  ])("recusa %o", (alteracao, campo, mensagem) => {
    expect(validarProduto({ ...VALIDO, ...alteracao })[campo]).toContain(mensagem);
  });

  it("aceita preço com ponto ou vírgula", () => {
    expect(validarProduto({ ...VALIDO, preco: "10.5" })).toEqual({});
    expect(validarProduto({ ...VALIDO, preco: "10" })).toEqual({});
  });
});

describe("validarMovimentacao", () => {
  it.each(["", "0", "-2", "1.5", "abc"])("recusa quantidade %s", (quantidade) => {
    expect(validarMovimentacao({ quantidade }).quantidade).toBeDefined();
  });

  it("aceita inteiro positivo", () => {
    expect(validarMovimentacao({ quantidade: "3" })).toEqual({});
  });
});

describe("paraApi", () => {
  it("converte os campos do formulário para o JSON da API", () => {
    expect(
      paraApi({ nome: " Caneta ", descricao: "  ", preco: "2,50", estoque_minimo: "5" }),
    ).toEqual({ nome: "Caneta", descricao: null, preco: "2.50", estoque_minimo: 5 });
  });
});
