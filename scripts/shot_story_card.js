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
  await page.goto("http://127.0.0.1:8891/index.html?v=10", { waitUntil: "load", timeout: 30000 });
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = "auto";
    document.querySelector("#story").scrollIntoView();
  });
  await page.waitForFunction(() => {
    const img = document.querySelector(".story-card img");
    return img && img.naturalWidth > 0;
  }, { timeout: 8000 });
  const sizes = await page.$$eval(".story-card img", (els) =>
    els.map((img) => `${img.getAttribute("src")} ${img.naturalWidth}x${img.naturalHeight}`)
  );
  const card = await page.$(".story-card");
  await card.screenshot({ path: "f:/강아지보호소품으로/data/shots/story-card.png" });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/stories-view.png" });
  await page.goto("http://127.0.0.1:8891/pets/index.html?v=11", { waitUntil: "load", timeout: 30000 });
  await Promise.all([
    page.waitForNavigation({ waitUntil: "load" }),
    page.click("nav a[href='../index.html#story']"),
  ]);
  const heading = await page.evaluate(() => {
    const node = document.querySelector("#story h2");
    const rect = node.getBoundingClientRect();
    return { text: node.textContent, top: Math.round(rect.top) };
  });
  console.log(sizes.join("\n"));
  console.log("heading", JSON.stringify(heading));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
