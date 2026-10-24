const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto("http://127.0.0.1:8891/index.html?v=bands", { waitUntil: "load", timeout: 30000 });
  await page.addStyleTag({ content: "html { scroll-behavior: auto !important; }" });
  const info = await page.evaluate(() => {
    const wrap = document.querySelector(".wrap");
    const ids = ["rehome", "waiting", "adopt-steps", "story", "contact"];
    const bands = ids.map((id) => {
      const el = document.getElementById(id);
      const style = getComputedStyle(el);
      return {
        id,
        width: Math.round(el.getBoundingClientRect().width),
        bg: style.backgroundColor,
      };
    });
    return {
      wrap: Math.round(wrap.getBoundingClientRect().width),
      cols: getComputedStyle(document.querySelector(".grid")).gridTemplateColumns.split(" ").length,
      stories: getComputedStyle(document.querySelector(".story-grid")).gridTemplateColumns.split(" ").length,
      bands,
    };
  });
  console.log(JSON.stringify(info));
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/band-hero.png" });
  for (const id of ["waiting", "adopt-steps", "story", "contact"]) {
    await page.evaluate((target) => {
      document.getElementById(target).scrollIntoView();
    }, id);
    await new Promise((resolve) => setTimeout(resolve, 200));
    await page.screenshot({ path: `f:/강아지보호소품으로/data/shots/band-${id}.png` });
  }
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
