// Render Gino's scorecard: node scorecard/render.js DIR  ->  DIR/scorecard.png (reads DIR/card.json).
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

(async () => {
  const dir = path.resolve(process.argv[2]);
  const card = JSON.parse(fs.readFileSync(path.join(dir, "card.json"), "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 640, height: 200 }, deviceScaleFactor: 2 });
  await page.addInitScript(c => { window.CARD = c; }, card);
  await page.goto("file://" + path.join(__dirname, "card.html"));
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(dir, "scorecard.png"), fullPage: true });
  await browser.close();
  console.log(path.join(dir, "scorecard.png"));
})();
