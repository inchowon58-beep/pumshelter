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
  await page.goto("http://127.0.0.1:8891/index.html?v=12", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => { document.documentElement.style.scrollBehavior = "auto"; });
  const nav = await page.$eval(".nav-links", (el) => el.innerText.replace(/\s+/g, " ").trim());
  const phoneInNav = await page.$(".nav-phone");
  const contact = await page.$(".contact-band");
  await contact.screenshot({ path: "f:/강아지보호소품으로/data/shots/contact-home.png" });
  await page.evaluate(() => document.querySelector(".grid .card").scrollIntoView({ block: "center" }));
  const card = await page.$(".grid .card");
  await card.screenshot({ path: "f:/강아지보호소품으로/data/shots/pet-card-react.png" });

  const href = await page.$eval(".grid .card a", (el) => el.getAttribute("href"));
  await page.goto("http://127.0.0.1:8891/" + href + "?v=12", { waitUntil: "load", timeout: 30000 });
  const comments = await page.$(".comment-box");
  await comments.screenshot({ path: "f:/강아지보호소품으로/data/shots/comments.png" });
  const stats = await page.$eval(".comment-box", (el) => ({
    heading: el.querySelector("h2").textContent,
    items: el.querySelectorAll("li").length,
  }));

  await page.setViewport({ width: 390, height: 844 });
  await page.goto("http://127.0.0.1:8891/index.html?v=13", { waitUntil: "load", timeout: 30000 });
  await page.click(".nav-toggle");
  await page.waitForSelector(".nav-links.is-open");
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/nav-mobile.png" });
  const open = await page.$eval(".nav-links", (el) => el.innerText.replace(/\s+/g, " ").trim());

  console.log(JSON.stringify({ nav, phoneInNav: Boolean(phoneInNav), stats, open }));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
