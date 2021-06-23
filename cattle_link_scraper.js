const puppeteer = require("puppeteer");
const fs = require("fs");

function run(offset) {
  return new Promise(async (resolve, reject) => {
    try {
      const browser = await puppeteer.launch({ headless: true });
      const page = await browser.newPage();
      await page.goto(
        `https://qurbani.bengalmeat.com/cattle/all?limit=1&offset=${offset}`,
        {
          waitUntil: "networkidle2",
        }
      );
      await page.waitForSelector("body");
      let urls = await page.evaluate(() => {
        let results = {};
        let items = document.querySelectorAll("div.cattle__featured__card");
        items.forEach((item) => {
          item.lastChild.click();
          results = {
            url: window.location.href,
            html: document.documentElement.outerHTML,
          };
        });
        return JSON.stringify(results);
      });
      await page.waitFor(5000);
      browser.close();
      fs.writeFile(__dirname + `/bm_cache/card_${offset}.txt`, urls, (err) => {
        if (err) throw err;
        console.log('File saved!');
      });
      return resolve(urls);
    } catch (e) {
      return reject(e);
    }
  });
}

let offset = process.argv[2];
run(offset).then(console.log).catch(console.error);

// console.log(final_results);



// const { Cluster } = require("puppeteer-cluster");
// const fs = require("fs").promises;

// (async () => {
//   const cluster = await Cluster.launch({
//     concurrency: Cluster.CONCURRENCY_CONTEXT,
//     maxConcurrency: 1,
//     monitor: true,
//   });

//   await cluster.task(async ({ page, data: url }) => {
//     await page.goto(url, {
//       waitUntil: "networkidle2",
//     });
//     await page.waitForSelector("body");
//     const stock = await page.evaluate(() => {
//       let allPosts = document.body.querySelectorAll(
//         "div.cattle__featured__card"
//       );
//       scrapeItems = [];
//       allPosts.forEach((item) => {
//         item.lastChild.click();
//         scrapeItems.push({
//             url: window.location.href,
//             html: document.documentElement.outerHTML,
//         });
//       });
//       let items = { items: scrapeItems };
//       return items;
//     });
//     console.log(stock);
//   });

//   cluster.on("taskerror", (err, data) => {
//     console.log(`Error crawling ${data}: ${err.message}`);
//   });

//   const csvFile = await fs.readFile(__dirname + "/bm_pages.csv", "utf8");
//   const lines = csvFile.split("\n");
//   for (let i = 0; i < lines.length; i++) {
//     const line = lines[i];
//     const splitterIndex = line.indexOf(",");
//     if (splitterIndex !== -1) {
//       const domain = line.substr(splitterIndex + 1);
//       console.log(domain);
//       cluster.queue(domain);
//     }
//   }

//   await cluster.idle();
//   await cluster.close();
// })();

