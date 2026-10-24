const puppeteer = require("puppeteer-core");

async function main() {
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    headless: true,
    args: ["--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport({ width: 1280, height: 860 });
  await page.goto("http://127.0.0.1:8891/index.html?v=contact", { waitUntil: "load", timeout: 30000 });
  await page.addStyleTag({ content: "html { scroll-behavior: auto !important; }" });
  await page.screenshot({ path: "f:/강아지보호소품으로/data/shots/nav-logo.png", clip: { x: 0, y: 0, width: 1280, height: 120 } });
  await page.evaluate(() => document.getElementById("contact").scrollIntoView());
  await new Promise((resolve) => setTimeout(resolve, 250));
  const box = await page.$("#contact");
  await box.screenshot({ path: "f:/강아지보호소품으로/data/shots/contact-band.png" });
  const motion = await page.evaluate(() => {
    const heart = document.querySelector(".contact-call.adopt .call-ico svg");
    const ring = document.querySelector(".call-ico .ring");
    return {
      heart: getComputedStyle(heart).animationName,
      ring: getComputedStyle(ring).animationName,
      footer: document.querySelector("footer .wrap").textContent.trim(),
    };
  });
  console.log(JSON.stringify(motion));
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
