const puppeteer = require("puppeteer"); // v 1.1.0
const { URL } = require("url");
const fse = require("fs-extra"); // v 5.0.0
const path = require("path");

async function start(urlToFetch, outputPathCounter) {
  /* 1 */
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  /* 2 */
  page.on("response", async (response) => {
    const url = new URL(response.url());
    let outputPath = `./bm_outputs/${outputPathCounter}`;
    let filePath = path.resolve(`${outputPath}/output${url.pathname}`);
    if (path.extname(url.pathname).trim() === "") {
      filePath = `${filePath}/index.html`;
    }
    await fse.outputFile(filePath, await response.buffer());
  });

  /* 3 */
  await page.goto(urlToFetch, {
    waitUntil: "networkidle2",
  });

  /* 4 */
  setTimeout(async () => {
    await browser.close();
  }, 60000 * 0.5);
}

start(process.argv[2], process.argv[3]);

// start('https://qurbani.bengalmeat.com/cattle/d8a2b97d-55fb-4d26-9c48-f7f1f508a369')
