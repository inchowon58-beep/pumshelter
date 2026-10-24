const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1360, height: 980 });
  await page.goto("http://127.0.0.1:8891/index.html?v=6", { waitUntil: "load", timeout: 30000 });
  await page.waitForSelector(".reason-card img");
  await page.waitForSelector(".callbar");
  const intro = await page.$(".rehome-intro");
  await intro.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-intro.png" });
  const quote = await page.$(".rehome-quote");
  await quote.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-quote.png" });
  await page.evaluate(() => document.querySelector(".rehome-quote").scrollIntoView({ block: "center" }));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-quote-view.png" });
  const reasons = await page.$(".reason-grid");
  await reasons.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-reasons.png" });
  const step = await page.$(".rehome-step");
  await step.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-step.png" });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-desk.png" });
  const imgs = await page.$$eval("#rehome img", (els) =>
    els.map((el) => `${el.getAttribute("src")} ${el.naturalWidth}x${el.naturalHeight}`)
  );
  const text = await page.$eval("#rehome", (el) => el.innerText);
  await page.setViewport({ width: 390, height: 900 });
  await page.evaluate(() => document.querySelector(".rehome-quote").scrollIntoView({ block: "center" }));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/rehome-mobile.png" });
  console.log(imgs.join("\n"));
  console.log("---");
  console.log(text.slice(0, 700));
  const before = await page.evaluate(() => {
    const rehome = document.querySelector("#rehome");
    const pets = [...document.querySelectorAll("h2")].find((node) => node.textContent.includes("가족을 기다리는"));
    return rehome && pets ? rehome.compareDocumentPosition(pets) : 0;
  });
  console.log("pets follow rehome", (before & 4) === 4);
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
