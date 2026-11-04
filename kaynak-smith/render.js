// HTML -> PDF (Chromium ile)
//   node render.js            -> kaynak_smith.html    -> Kaynak_Smith_Diyagrami.pdf
//   node render.js ornekler   -> kaynak_ornekler.html -> Kaynak_Ornekler_Smith_Faktorler.pdf
const { chromium } = require('playwright');
const path = require('path');

const JOBS = {
  smith: ['kaynak_smith.html', 'Kaynak_Smith_Diyagrami.pdf', 'Kaynak Dikişi ve Smith Diyagramı'],
  ornekler: ['kaynak_ornekler.html', 'Kaynak_Ornekler_Smith_Faktorler.pdf', 'Kaynak Örnekleri: Smith + Dikiş Faktörleri'],
};

(async () => {
  const [src, out, title] = JOBS[process.argv[2] || 'smith'];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, src), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(__dirname, out),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      '<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#8a929b;padding:0 17mm;display:flex;justify-content:space-between;">' +
      `<span>${title} · Makina Elemanları I</span>` +
      '<span>Sayfa <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  await browser.close();
  console.log('PDF yazıldı:', out);
})();
