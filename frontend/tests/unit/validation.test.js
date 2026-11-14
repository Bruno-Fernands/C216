import { describe, expect, it } from "vitest";
import { DESCRICAO_MAX, NOME_MAX, NOME_MIN, validarItem } from "../../src/validation.js";

describe("validarItem", () => {
  it("aceita um item válido", () => {
    expect(validarItem({ nome: "Caderno", descricao: "Capa azul" })).toEqual({});
  });

  it("exige nome e descrição", () => {
    const erros = validarItem({ nome: "", descricao: "" });
    expect(erros.nome).toMatch(/obrigatório/);
    expect(erros.descricao).toMatch(/obrigatória/);
  });

  it("trata texto só com espaços como vazio", () => {
    expect(validarItem({ nome: "   ", descricao: "  " })).toHaveProperty("nome");
  });

  it("valida os limites do nome", () => {
    expect(validarItem({ nome: "a".repeat(NOME_MIN - 1), descricao: "x" }).nome).toMatch(
      /pelo menos/,
    );
    expect(validarItem({ nome: "a".repeat(NOME_MIN), descricao: "x" })).toEqual({});
    expect(validarItem({ nome: "a".repeat(NOME_MAX), descricao: "x" })).toEqual({});
    expect(validarItem({ nome: "a".repeat(NOME_MAX + 1), descricao: "x" }).nome).toMatch(
      /no máximo/,
    );
  });

  it("valida o limite da descrição", () => {
    expect(validarItem({ nome: "Item", descricao: "d".repeat(DESCRICAO_MAX) })).toEqual({});
    expect(
      validarItem({ nome: "Item", descricao: "d".repeat(DESCRICAO_MAX + 1) }).descricao,
    ).toMatch(/no máximo/);
  });

  it("não quebra quando os campos faltam", () => {
    expect(Object.keys(validarItem({}))).toEqual(["nome", "descricao"]);
  });
});
