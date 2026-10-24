const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1680, height: 1000 });
  await page.goto("http://127.0.0.1:8891/index.html?v=wide", { waitUntil: "load", timeout: 30000 });
  const width = await page.$eval(".wrap", (el) => Math.round(el.getBoundingClientRect().width));
  const cols = await page.$eval(".grid", (el) => getComputedStyle(el).gridTemplateColumns.split(" ").length);
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/wide-home.png" });
  console.log(JSON.stringify({ width, cols }));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
