import { expect, test } from "@playwright/test";

// Os projetos (desktop/mobile) rodam em paralelo no mesmo banco: o nome
// precisa ser único por teste para um não esbarrar no outro.
function nomeUnico(testInfo, prefixo) {
  return `${prefixo} ${testInfo.project.name} ${Date.now()}`;
}

async function abrir(page) {
  await page.goto("/");
  await expect(page.getByRole("status")).toBeHidden(); // terminou de carregar
}

async function cadastrar(page, nome, preco = "2,50", minimo = "5") {
  await page.getByLabel("Nome", { exact: true }).fill(nome);
  await page.getByLabel("Preço (R$)").fill(preco);
  await page.getByLabel("Estoque mínimo").fill(minimo);
  const [post] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/produtos") && r.request().method() === "POST"),
    page.getByRole("button", { name: "Cadastrar" }).click(),
  ]);
  expect(post.status()).toBe(201);
  return post;
}

async function movimentar(page, tipo, quantidade, observacao = "") {
  const painel = page.getByRole("region", { name: "Movimentações" });
  await painel.getByLabel(tipo).check();
  await painel.getByLabel("Quantidade").fill(String(quantidade));
  await painel.getByLabel("Observação (opcional)").fill(observacao);
  await painel.getByRole("button", { name: "Registrar" }).click();
  return painel;
}

test("cadastra, movimenta e os dados persistem após recarregar", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Caneta");
  await abrir(page);

  const post = await cadastrar(page, nome);
  const { id } = await post.json(); // lido já: o corpo some após o reload
  // CORS: a API responde liberando exatamente a origem do frontend.
  const origem = new URL(page.url()).origin;
  expect(post.headers()["access-control-allow-origin"]).toBe(origem);

  const item = page.getByRole("listitem", { name: nome });
  await expect(item.getByText("Estoque baixo")).toBeVisible(); // saldo 0 < mínimo 5

  await item.getByRole("button", { name: "Movimentar" }).click();
  const painel = await movimentar(page, "Entrada", 10, "Compra do fornecedor");
  await expect(page.getByText("Entrada registrada.")).toBeVisible();
  await movimentar(page, "Saída", 4, "Venda balcão");
  await expect(painel.getByText("Saldo atual: 6")).toBeVisible();
  await expect(painel.getByRole("list", { name: "Histórico" }).getByRole("listitem")).toHaveCount(
    2,
  );
  await expect(item.getByText("Estoque baixo")).toBeHidden(); // 6 >= 5

  // Persistência: depois de recarregar, tudo vem de novo do PostgreSQL.
  await page.reload();
  await expect(page.getByRole("status")).toBeHidden();
  const recarregado = page.getByRole("listitem", { name: nome });
  await expect(recarregado.getByText("6", { exact: true })).toBeVisible();
  await recarregado.getByRole("button", { name: "Movimentar" }).click();
  await expect(page.getByText("Compra do fornecedor")).toBeVisible();
  await expect(page.getByText("Venda balcão")).toBeVisible();

  // E conferindo direto na API.
  const produto = await (
    await page.request.get(`${new URL(post.url()).origin}/produtos/${id}`)
  ).json();
  expect(produto.quantidade).toBe(6);
});

test("saída maior que o saldo é recusada pela API", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Caderno");
  await abrir(page);
  await cadastrar(page, nome);

  await page
    .getByRole("listitem", { name: nome })
    .getByRole("button", { name: "Movimentar" })
    .click();
  await movimentar(page, "Entrada", 2);
  const painel = await movimentar(page, "Saída", 5);

  await expect(page.getByRole("alert")).toHaveText(
    "Estoque insuficiente: disponível 2, solicitado 5.",
  );
  await expect(painel.getByText("Saldo atual: 2")).toBeVisible();
});

test("edita e exclui um produto", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Lápis");
  const novoNome = `${nome} HB`;
  await abrir(page);
  await cadastrar(page, nome);

  await page.getByRole("listitem", { name: nome }).getByRole("button", { name: "Editar" }).click();
  await page.getByLabel("Nome", { exact: true }).fill(novoNome);
  await page.getByLabel("Preço (R$)").fill("1,75");
  await page.getByRole("button", { name: "Salvar alterações" }).click();
  const editado = page.getByRole("listitem", { name: novoNome });
  await expect(editado.getByText("R$ 1,75")).toBeVisible();

  page.once("dialog", (dialogo) => dialogo.accept());
  await editado.getByRole("button", { name: "Excluir" }).click();
  await expect(page.getByText("Produto excluído.")).toBeVisible();

  await page.reload();
  await expect(page.getByRole("status")).toBeHidden();
  await expect(page.getByRole("listitem", { name: novoNome })).toHaveCount(0);
});

test("busca por nome filtra a lista", async ({ page }, testInfo) => {
  const nome = nomeUnico(testInfo, "Grampeador");
  await abrir(page);
  await cadastrar(page, nome);

  await page.getByLabel("Buscar por nome").fill(nome);
  await expect(page.getByRole("list", { name: "Produtos" }).getByRole("listitem")).toHaveCount(1);
  await page.getByLabel("Buscar por nome").fill(`${nome} inexistente`);
  await expect(page.getByText("Nenhum produto encontrado.")).toBeVisible();
});

test("layout responsivo sem rolagem horizontal", async ({ page }) => {
  await abrir(page);
  const largura = await page.evaluate(() => document.documentElement.scrollWidth);
  expect(largura).toBeLessThanOrEqual(page.viewportSize().width);
});
