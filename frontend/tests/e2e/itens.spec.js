import { expect, test } from "@playwright/test";

// Os projetos (desktop/mobile) rodam em paralelo no mesmo banco: o nome
// precisa ser único por teste para um não esbarrar no outro.
function nomeUnico(testInfo) {
  return `Item ${testInfo.project.name} ${Date.now()}`.slice(0, 50);
}

test("cadastra um item e ele continua lá após recarregar a página", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo);
  await page.goto("/");
  await expect(page.getByRole("status")).toBeHidden(); // terminou de carregar

  await page.getByLabel("Nome").fill(nome);
  await page.getByLabel("Descrição").fill("Criado pelo teste E2E");

  const [post] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/items/") && r.request().method() === "POST"),
    page.getByRole("button", { name: "Adicionar" }).click(),
  ]);
  const origem = new URL(page.url()).origin;
  expect(post.status()).toBe(201);
  expect(post.headers()["access-control-allow-origin"]).toBe(origem);

  // O Chromium não expõe o preflight nos eventos da página, então o OPTIONS
  // que o navegador fez é repetido aqui com os mesmos cabeçalhos.
  const preflight = await page.request.fetch(post.url(), {
    method: "OPTIONS",
    headers: {
      Origin: origem,
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "content-type",
    },
  });
  expect(preflight.status()).toBe(200);
  expect(preflight.headers()["access-control-allow-origin"]).toBe(origem);

  const lista = page.getByRole("list", { name: "Itens cadastrados" });
  await expect(lista.getByRole("heading", { name: nome })).toBeVisible();

  await page.reload();
  await expect(lista.getByRole("heading", { name: nome })).toBeVisible();
});

test("nome repetido mostra a mensagem da API", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo);
  await page.goto("/");

  for (let i = 0; i < 2; i++) {
    await page.getByLabel("Nome").fill(nome);
    await page.getByLabel("Descrição").fill(`Tentativa ${i + 1}`);
    await page.getByRole("button", { name: "Adicionar" }).click();
    // Espera o primeiro salvar (e limpar o formulário) antes de repetir.
    if (i === 0) await expect(page.getByRole("heading", { name: nome })).toBeVisible();
  }

  await expect(page.getByRole("alert")).toHaveText("Já existe um item com esse nome");
  await expect(page.getByRole("heading", { name: nome })).toHaveCount(1);
});

test("validação no navegador não chama a API", async ({ page }) => {
  await page.goto("/");
  let posts = 0;
  page.on("request", (r) => r.method() === "POST" && posts++);

  await page.getByRole("button", { name: "Adicionar" }).click();

  await expect(page.getByRole("alert")).toHaveCount(2);
  expect(posts).toBe(0);
});

test("layout responsivo sem rolagem horizontal", async ({ page }) => {
  await page.goto("/");
  const largura = await page.evaluate(() => document.documentElement.scrollWidth);
  expect(largura).toBeLessThanOrEqual(page.viewportSize().width);
});
