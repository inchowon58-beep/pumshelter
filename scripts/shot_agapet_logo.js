const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 500 });
  await page.goto("https://www.agapetstory.co.kr/", { waitUntil: "networkidle2", timeout: 45000 });
  const header = await page.$("header");
  if (header) {
    await header.screenshot({ path: "f:/강아지보호소품으로/data/shots/agapet-header.png" });
  } else {
    await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/agapet-header.png" });
  }
  const logos = await page.evaluate(() =>
    [...document.images].slice(0, 12).map((img) => ({ src: img.src, alt: img.alt, w: img.width, h: img.height }))
  );
  console.log(JSON.stringify(logos, null, 2));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
