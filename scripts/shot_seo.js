const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto("http://127.0.0.1:8891/area/seoul/?v=seo", { waitUntil: "load", timeout: 30000 });
  await page.addStyleTag({ content: "html { scroll-behavior: auto !important; }" });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/seo-top.png" });
  await page.evaluate(() => document.querySelector(".seo-article").scrollIntoView());
  await new Promise((resolve) => setTimeout(resolve, 200));
  const article = await page.$(".seo-article");
  await article.screenshot({ path: "f:/강아지보호소품으로/data/shots/seo-article.png" });
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
