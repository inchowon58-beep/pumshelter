const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1360, height: 900 });
  await page.goto("http://127.0.0.1:8891/index.html?v=hero", { waitUntil: "load", timeout: 30000 });
  const hero = await page.$(".hero-photos");
  await hero.screenshot({ path: "f:/강아지보호소품으로/data/shots/hero-react.png" });
  const labels = await page.$$eval(".hero-name", (nodes) => nodes.map((node) => node.innerText.replace(/\s+/g, " ").trim()));
  await page.setViewport({ width: 390, height: 844 });
  await page.goto("http://127.0.0.1:8891/index.html?v=hero-m", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => document.querySelector(".hero-photos").scrollIntoView({ block: "center" }));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/hero-react-mobile.png" });
  console.log(labels.join(" | "));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
