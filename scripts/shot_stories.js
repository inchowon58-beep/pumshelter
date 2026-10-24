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

  await page.goto("http://127.0.0.1:8891/pets/index.html?v=7", { waitUntil: "load", timeout: 30000 });
  const gap = await page.evaluate(() => {
    const lede = document.querySelector(".board-hero .lede");
    const photo = document.querySelector(".card-photo");
    const lr = lede.getBoundingClientRect();
    const pr = photo.getBoundingClientRect();
    return Math.round(pr.top - lr.bottom);
  });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/board-gap.png" });

  await page.goto("http://127.0.0.1:8891/index.html?v=9", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => { document.documentElement.style.scrollBehavior = "auto"; });
  const count = await page.$$eval(".story-card", (els) => els.length);
  const order = await page.evaluate(() => {
    const steps = document.querySelector("#adopt-steps");
    const story = document.querySelector("#story");
    const contact = document.querySelector("#contact");
    return steps.compareDocumentPosition(story) === 4 && story.compareDocumentPosition(contact) === 4;
  });
  const story = await page.$("#story");
  await story.screenshot({ path: "f:/강아지보호소품으로/data/shots/stories-home.png" });
  const contact = await page.$(".contact-band");
  await contact.screenshot({ path: "f:/강아지보호소품으로/data/shots/contact-home.png" });
  console.log("order", order);

  await page.goto("http://127.0.0.1:8891/stories/11/index.html?v=7", { waitUntil: "load", timeout: 30000 });
  const storyBits = await page.evaluate(() => ({
    title: document.querySelector("h1").textContent,
    images: document.querySelectorAll(".story-photos img").length,
    lines: document.querySelectorAll(".story-text span").length,
  }));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/story-detail.png" });

  await page.setViewport({ width: 390, height: 900 });
  await page.goto("http://127.0.0.1:8891/pets/index.html?v=8", { waitUntil: "load", timeout: 30000 });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/board-gap-mobile.png" });
  await page.goto("http://127.0.0.1:8891/index.html?v=8#contact", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => document.querySelector("#contact").scrollIntoView({ block: "start" }));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/contact-mobile.png" });

  console.log(JSON.stringify({ gap, count, storyBits }));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
