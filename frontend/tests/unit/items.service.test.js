import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createItem, listItems } from "../../src/services/items.js";
import { resposta } from "../respostas.js";

describe("services/items", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it("listItems faz GET em /items/ e devolve o JSON", async () => {
    const itens = [{ id: 1, nome: "Caderno", descricao: "Azul" }];
    fetch.mockReturnValue(resposta(200, itens));

    await expect(listItems()).resolves.toEqual(itens);
    expect(fetch).toHaveBeenCalledWith("http://localhost:8000/items/", undefined);
  });

  it("createItem faz POST com JSON", async () => {
    fetch.mockReturnValue(resposta(201, { id: 1, nome: "Caderno", descricao: "Azul" }));

    await createItem({ nome: "Caderno", descricao: "Azul" });

    const [url, opcoes] = fetch.mock.calls[0];
    expect(url).toBe("http://localhost:8000/items/");
    expect(opcoes.method).toBe("POST");
    expect(opcoes.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(opcoes.body)).toEqual({ nome: "Caderno", descricao: "Azul" });
  });

  it("usa o detail da API como mensagem de erro", async () => {
    fetch.mockReturnValue(resposta(409, { detail: "Já existe um item com esse nome" }));
    await expect(createItem({ nome: "a", descricao: "b" })).rejects.toThrow(
      "Já existe um item com esse nome",
    );
  });

  it("usa mensagem genérica quando o detail não é texto (422) ou não há corpo", async () => {
    fetch.mockReturnValue(resposta(422, { detail: [{ msg: "x" }] }));
    await expect(createItem({ nome: "a", descricao: "b" })).rejects.toThrow("Erro 422");

    fetch.mockReturnValue(
      Promise.resolve({ ok: false, status: 500, json: () => Promise.reject(new Error()) }),
    );
    await expect(listItems()).rejects.toThrow("Erro 500");
  });

  it("avisa quando o servidor está fora do ar", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(listItems()).rejects.toThrow("Não foi possível conectar ao servidor.");
  });
});
