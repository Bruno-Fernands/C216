import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  atualizarProduto,
  criarProduto,
  listarProdutos,
  registrarMovimentacao,
  removerProduto,
} from "../../src/services/produtos.js";
import { resposta } from "../respostas.js";

const API = "http://localhost:8000";

describe("services/produtos", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it("listarProdutos monta a query string só com os filtros usados", async () => {
    fetch.mockReturnValue(resposta(200, []));

    await listarProdutos();
    await listarProdutos({ busca: " can ", abaixoDoMinimo: true });

    expect(fetch.mock.calls[0][0]).toBe(`${API}/produtos`);
    expect(fetch.mock.calls[1][0]).toBe(`${API}/produtos?busca=can&abaixo_do_minimo=true`);
  });

  it("criar e atualizar enviam JSON com o método certo", async () => {
    fetch.mockReturnValue(resposta(200, { id: 1 }));

    await criarProduto({ nome: "Caneta" });
    await atualizarProduto(1, { nome: "Lápis" });

    expect(fetch.mock.calls[0][0]).toBe(`${API}/produtos`);
    expect(fetch.mock.calls[0][1].method).toBe("POST");
    expect(fetch.mock.calls[1][0]).toBe(`${API}/produtos/1`);
    expect(fetch.mock.calls[1][1].method).toBe("PUT");
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ nome: "Lápis" });
  });

  it("removerProduto aceita 204 sem corpo", async () => {
    fetch.mockReturnValue(
      Promise.resolve({ ok: true, status: 204, json: () => Promise.reject(new Error()) }),
    );
    await expect(removerProduto(3)).resolves.toBeNull();
    expect(fetch).toHaveBeenCalledWith(`${API}/produtos/3`, { method: "DELETE" });
  });

  it("usa o detail da API como mensagem de erro", async () => {
    fetch.mockReturnValue(resposta(409, { detail: "Estoque insuficiente" }));
    await expect(registrarMovimentacao(1, { tipo: "saida", quantidade: 9 })).rejects.toThrow(
      "Estoque insuficiente",
    );
  });

  it("mensagem genérica quando o erro não tem detail em texto (422)", async () => {
    fetch.mockReturnValue(resposta(422, { detail: [{ msg: "x" }] }));
    await expect(listarProdutos()).rejects.toThrow("Erro 422");
  });

  it("mensagem amigável quando o servidor está fora do ar", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(listarProdutos()).rejects.toThrow("Não foi possível conectar");
  });
});
