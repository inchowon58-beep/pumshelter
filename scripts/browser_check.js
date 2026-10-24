const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

const shots = path.join("f:\\강아지보호소품으로", "data", "shots");
const edge = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const base = "http://127.0.0.1:8891";

async function main() {
  const browser = await puppeteer.launch({
    executablePath: edge,
    headless: true,
    args: ["--disable-gpu", "--font-render-hinting=none"],
  });
  const page = await browser.newPage();
  const notes = [];

  await page.setViewport({ width: 1360, height: 980 });
  await page.goto(`${base}/index.html`, { waitUntil: "load", timeout: 30000 });
  const homeTitle = await page.title();
  notes.push(`home title ${homeTitle}`);
  await page.screenshot({ path: path.join(shots, "view-home.png") });

  await page.setViewport({ width: 390, height: 844 });
  await page.screenshot({ path: path.join(shots, "view-mobile.png") });

  await page.setViewport({ width: 1360, height: 1100 });
  await page.goto(`${base}/pets/index.html`, { waitUntil: "load", timeout: 30000 });
  await page.screenshot({ path: path.join(shots, "view-pets.png") });
  await page.setViewport({ width: 390, height: 900 });
  await page.screenshot({ path: path.join(shots, "view-pets-mobile.png") });
  await page.setViewport({ width: 1360, height: 1100 });
  const initial = await page.$eval("#count", (el) => el.textContent.trim());
  notes.push(`initial count ${initial}`);

  await page.click('[data-filter="waiting"]');
  const waiting = await page.$eval("#count", (el) => el.textContent.trim());
  const waitingVisible = await page.$$eval("[data-pet]", (els) => els.filter((el) => !el.hidden).length);
  notes.push(`waiting ${waiting} visible ${waitingVisible}`);

  await page.click('[data-filter="adopted"]');
  const adoptedVisible = await page.$$eval("[data-pet]", (els) => els.filter((el) => !el.hidden).length);
  notes.push(`adopted visible ${adoptedVisible}`);

  await page.click('[data-filter="all"]');
  await page.type("#q", "쫑이");
  const searchVisible = await page.$$eval("[data-pet]", (els) =>
    els.filter((el) => !el.hidden).map((el) => el.dataset.name)
  );
  notes.push(`search 쫑이 ${searchVisible.join(",")}`);

  await page.goto(`${base}/pets/8cbb1b29-d1c3-4e4b-891a-e7f5f31df167/index.html`, {
    waitUntil: "load",
    timeout: 30000,
  });
  const before = await page.$eval("#hero-photo", (img) => img.getAttribute("src"));
  await page.click('.thumbs button:nth-child(2)');
  const after = await page.$eval("#hero-photo", (img) => img.getAttribute("src"));
  const alt = await page.$eval("#hero-photo", (img) => img.alt);
  notes.push(`gallery ${before.endsWith("/0.jpg")} -> ${after.endsWith("/1.jpg")} alt ${alt}`);
  await page.screenshot({ path: path.join(shots, "view-detail.png") });

  await Promise.all([
    page.waitForNavigation({ waitUntil: "load", timeout: 15000 }),
    page.click("a.btn.btn-ghost"),
  ]);
  notes.push(`back ${page.url().endsWith("/pets/index.html")}`);

  await browser.close();
  const report = notes.join("\n");
  fs.writeFileSync(path.join("f:\\강아지보호소품으로", "data", "browser-check.txt"), report, "utf8");
  console.log(report);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
