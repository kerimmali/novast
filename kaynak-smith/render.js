// kaynak_smith.html -> Kaynak_Smith_Diyagrami.pdf (Chromium ile)
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'kaynak_smith.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(__dirname, 'Kaynak_Smith_Diyagrami.pdf'),
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      '<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#8a929b;padding:0 17mm;display:flex;justify-content:space-between;">' +
      '<span>Kaynak Dikişi ve Smith Diyagramı · Makina Elemanları I</span>' +
      '<span>Sayfa <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  await browser.close();
  console.log('PDF yazıldı.');
})();
