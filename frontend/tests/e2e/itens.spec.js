import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  // Critério de aceite: nenhuma requisição sai do próprio servidor do frontend.
  page.on("request", (req) => {
    expect(new URL(req.url()).origin).toBe("http://localhost:4173");
  });
  await page.goto("/");
});

test("fluxo completo: validar, adicionar e remover", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Gerenciador de Itens" })).toBeVisible();
  await expect(page.getByText("Nenhum item cadastrado.")).toBeVisible();

  await page.getByRole("button", { name: "Adicionar" }).click();
  await expect(page.getByRole("alert")).toHaveCount(2);

  await page.getByLabel("Nome").fill("Caderno");
  await page.getByLabel("Descrição").fill("Capa azul, 96 folhas");
  await page.getByRole("button", { name: "Adicionar" }).click();

  const lista = page.getByRole("list", { name: "Itens cadastrados" });
  await expect(lista.getByRole("listitem")).toHaveCount(1);
  await expect(lista).toContainText("Capa azul, 96 folhas");
  await expect(page.getByRole("alert")).toHaveCount(0);

  await page.getByRole("button", { name: "Remover Caderno" }).click();
  await expect(page.getByText("Nenhum item cadastrado.")).toBeVisible();
});

test("layout responsivo sem rolagem horizontal", async ({ page }) => {
  const largura = await page.evaluate(() => document.documentElement.scrollWidth);
  expect(largura).toBeLessThanOrEqual(page.viewportSize().width);
});
