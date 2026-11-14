// Monta uma resposta falsa no formato que `fetch` devolve.
export function resposta(status, corpo) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: async () => corpo });
}
