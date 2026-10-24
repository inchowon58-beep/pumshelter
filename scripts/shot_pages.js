const puppeteer = require("puppeteer-core");
const path = require("path");

const shots = path.join("f:\\강아지보호소품으로", "data", "shots");
const edge = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const base = "http://127.0.0.1:8891";

async function main() {
  const browser = await puppeteer.launch({
    executablePath: edge,
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1360, height: 980 });
  await page.goto(`${base}/index.html`, { waitUntil: "load" });
  const homeText = await page.evaluate(() => document.body.innerText);
  await page.screenshot({ path: path.join(shots, "home-now.png") });
  await page.goto(`${base}/pets/index.html`, { waitUntil: "load" });
  const cards = await page.$$eval("[data-pet]", (els) => els.filter((el) => !el.hidden).length);
  const listText = await page.evaluate(() => document.body.innerText);
  await page.screenshot({ path: path.join(shots, "list-now.png") });
  await page.goto(`${base}/pets/a4ba8c45-7f3c-40d6-aef1-5b523549b820/index.html`, { waitUntil: "load" });
  const detailText = await page.evaluate(() => document.body.innerText);
  await page.screenshot({ path: path.join(shots, "eunbi-now.png") });
  await browser.close();
  const banned = ["전체 기록", "현재 보호", "입양 완료", "입양 대기", "보호 시작일", "입양 가능"];
  const hit = (label, text) => banned.filter((word) => text.includes(word)).map((word) => `${label}:${word}`);
  console.log([
    `cards ${cards}`,
    ...hit("home", homeText),
    ...hit("list", listText),
    ...hit("detail", detailText),
    detailText.includes("똑순이") ? "eunbi blurb ok" : "eunbi blurb missing",
  ].join("\n"));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
