#!/usr/bin/env node
/* Builds every sellable file into ebook/dist/:
 *   - ebook PDF (8.5x8.5 in, covers included)  -> Gumroad, Payhip, Etsy, Google Play, Kindle Kids' Book Creator
 *   - print interior PDF with bleed            -> Amazon KDP paperback, Lulu
 *   - print wraparound cover PDF (with spine)  -> Amazon KDP paperback
 *   - front cover JPG (2560x2560)              -> store listings, marketing
 *   - fixed-layout EPUB 3                      -> Apple Books, Kobo, Google Play
 *   - preview sheet PNG                        -> quick look at every page
 * Usage: node ebook/build.js   (edit ebook/config.json first)
 */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const ROOT = __dirname, DIST = path.join(ROOT, 'dist');
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'config.json'), 'utf8'));
const src = fs.readFileSync(path.join(ROOT, '..', 'islamic-kids-storybook.html'), 'utf8');
const d0 = src.indexOf('<svg width="0"');
const sceneDefs = src.slice(d0, src.indexOf('</svg>', d0) + 6);
const storyScript = src.slice(src.indexOf('/* ---------- illustration toolkit'), src.indexOf('/* ---------- rendering'));
const FONTS = 'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Aref+Ruqaa:wght@400;700&family=Baloo+2:wght@600;700;800&family=Nunito:ital,wght@0,400;0,600;0,700;0,800;1,400&display=block';
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="${FONTS}">
<style>${fs.readFileSync(path.join(ROOT, 'book.css'), 'utf8')}</style><style id="pagesize"></style></head>
<body>${sceneDefs}<div id="book"></div><script>window.CFG=${JSON.stringify(cfg)};</script>
<script>${storyScript}</script><script>${fs.readFileSync(path.join(ROOT, 'book.js'), 'utf8')}</script></body></html>`;

const out = name => path.join(DIST, `${cfg.filePrefix}-${name}`);
const xml = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

(async () => {
  fs.rmSync(DIST, { recursive: true, force: true }); fs.mkdirSync(DIST, { recursive: true });
  const browser = await chromium.launch();
  const open = async (dsf = 1) => {
    const pg = await browser.newPage({ viewport: { width: 1800, height: 1000 }, deviceScaleFactor: dsf });
    pg.on('pageerror', e => { console.error('PAGE ERROR:', e.message); process.exitCode = 1; });
    await pg.setContent(html, { waitUntil: 'networkidle' });
    return pg;
  };
  const pdf = (pg, file, info) => pg.pdf({ path: file, width: info.w + 'px', height: info.h + 'px', printBackground: true, preferCSSPageSize: true });
  const report = (label, info) => { console.log(`${label}: ${info.count ?? 1} page(s), ${info.w}x${info.h}px`); (info.warn || []).forEach(w => console.warn('  WARNING ' + w)); };

  // 1. ebook PDF
  let pg = await open();
  let info = await pg.evaluate(() => BOOK.build('ebook')); report('ebook', info);
  await pdf(pg, out('ebook.pdf'), info);
  const ebook = info;

  // 2. print interior (8.625 x 8.75 in: bleed on top, bottom and outside edge)
  info = await pg.evaluate(() => BOOK.build('print')); report('print interior', info);
  await pdf(pg, out('print-interior.pdf'), info);
  const interiorPages = info.count;

  // 3. wraparound cover; spine width = pages x paper thickness
  const spineIn = interiorPages * cfg.paperThicknessIn;
  info = await pg.evaluate(s => BOOK.buildWrap(s), spineIn * 96); report('print cover', info);
  await pdf(pg, out('print-cover.pdf'), info);
  const coverIn = { w: (info.w / 96).toFixed(3), h: (info.h / 96).toFixed(3) };

  // 4. preview sheet
  await pg.setViewportSize({ width: 1800, height: 1000 });
  await pg.evaluate(() => BOOK.build('sheet'));
  await pg.screenshot({ path: out('preview-sheet.png'), fullPage: true });
  await pg.close();

  // 5. front cover JPG, 2560px square
  pg = await open(2560 / 816);
  await pg.evaluate(() => BOOK.build('front'));
  await (await pg.$('section.page')).screenshot({ path: out('front-cover.jpg'), type: 'jpeg', quality: 92 });
  await pg.close();

  // 6. fixed-layout EPUB 3, one 1600px image per page
  const SZ = 1600, ep = path.join(DIST, '.epub');
  ['META-INF', 'OEBPS/images', 'OEBPS/pages'].forEach(d => fs.mkdirSync(path.join(ep, d), { recursive: true }));
  pg = await open(SZ / 816);
  await pg.evaluate(() => BOOK.build('ebook'));
  const els = await pg.$$('section.page');
  const ids = els.map((_, i) => 'p' + String(i + 1).padStart(3, '0'));
  for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: path.join(ep, 'OEBPS/images', ids[i] + '.jpg'), type: 'jpeg', quality: 88 });
  await pg.close(); await browser.close();

  fs.writeFileSync(path.join(ep, 'mimetype'), 'application/epub+zip');
  fs.writeFileSync(path.join(ep, 'META-INF/container.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>`);
  ids.forEach((id, i) => fs.writeFileSync(path.join(ep, 'OEBPS/pages', id + '.xhtml'), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="${cfg.language}" lang="${cfg.language}">
<head><meta charset="UTF-8"/><title>${xml(cfg.title)} – page ${i + 1}</title><meta name="viewport" content="width=${SZ}, height=${SZ}"/>
<style>html,body{margin:0;padding:0;width:${SZ}px;height:${SZ}px;overflow:hidden}img{display:block;width:${SZ}px;height:${SZ}px}</style></head>
<body><img src="../images/${id}.jpg" alt="${xml(ebook.alts[i])}"/></body></html>`));
  const navItems = [{ i: 0, label: 'Cover' }, { i: 1, label: 'Title page' }, ...ebook.nav];
  fs.writeFileSync(path.join(ep, 'OEBPS/nav.xhtml'), `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="${cfg.language}" lang="${cfg.language}">
<head><meta charset="UTF-8"/><title>Contents</title></head><body>
<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>${navItems.map(n => `<li><a href="pages/${ids[n.i]}.xhtml">${xml(n.label)}</a></li>`).join('')}</ol></nav>
<nav epub:type="landmarks" hidden=""><ol><li><a epub:type="cover" href="pages/${ids[0]}.xhtml">Cover</a></li><li><a epub:type="bodymatter" href="pages/${ids[ebook.nav[0].i]}.xhtml">Start reading</a></li></ol></nav>
</body></html>`);
  const modified = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  fs.writeFileSync(path.join(ep, 'OEBPS/content.opf'), `<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="${cfg.language}" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">${xml(cfg.isbn ? 'urn:isbn:' + cfg.isbn : cfg.bookId)}</dc:identifier>
<dc:title>${xml(cfg.title)}: ${xml(cfg.subtitle)}</dc:title><dc:creator>${xml(cfg.author)}</dc:creator><dc:publisher>${xml(cfg.publisher)}</dc:publisher>
<dc:language>${cfg.language}</dc:language><dc:subject>Islamic stories for children</dc:subject>
<dc:description>Six true stories from the Qur'an, from Prophet Adam to Prophet Ibrahim, for children aged 5 to 10.</dc:description>
<meta property="dcterms:modified">${modified}</meta>
<meta property="rendition:layout">pre-paginated</meta><meta property="rendition:orientation">auto</meta><meta property="rendition:spread">none</meta>
<meta property="schema:accessMode">visual</meta><meta property="schema:accessModeSufficient">visual</meta><meta property="schema:accessibilityFeature">alternativeText</meta><meta property="schema:accessibilityHazard">none</meta>
<meta property="schema:accessibilitySummary">Each page is an illustrated image with alternative text containing the full page text.</meta>
<meta name="cover" content="cover-image"/>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
${ids.map((id, i) => `<item id="${i === 0 ? 'cover-image' : 'img-' + id}" href="images/${id}.jpg" media-type="image/jpeg"${i === 0 ? ' properties="cover-image"' : ''}/>
<item id="${id}" href="pages/${id}.xhtml" media-type="application/xhtml+xml"/>`).join('\n')}
</manifest>
<spine>${ids.map(id => `<itemref idref="${id}"/>`).join('')}</spine>
</package>`);
  execFileSync('python3', ['-c', `import sys,os,zipfile
src,dst=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(dst,'w')
z.write(os.path.join(src,'mimetype'),'mimetype',compress_type=zipfile.ZIP_STORED)
for root,dirs,files in os.walk(src):
    dirs.sort()
    for f in sorted(files):
        p=os.path.join(root,f);a=os.path.relpath(p,src)
        if a!='mimetype': z.write(p,a,compress_type=zipfile.ZIP_DEFLATED)
z.close()`, ep, out('fixed-layout.epub')]);
  fs.rmSync(ep, { recursive: true, force: true });

  fs.writeFileSync(path.join(DIST, 'print-specs.txt'), `Print specs (Amazon KDP paperback)
Trim size: 8.5 x 8.5 in, bleed, premium colour ink, white paper
Interior pages: ${interiorPages}
Spine width: ${spineIn.toFixed(4)} in (${interiorPages} pages x ${cfg.paperThicknessIn} in)
Cover PDF size: ${coverIn.w} x ${coverIn.h} in
No spine text (KDP allows spine text only from 79 pages).
Barcode: leave the area at the bottom right of the back cover clear; KDP adds the barcode there.
`);
  console.log('\nFiles in ebook/dist:'); fs.readdirSync(DIST).forEach(f => console.log(`  ${f}  ${(fs.statSync(path.join(DIST, f)).size / 1048576).toFixed(1)} MB`));
})().catch(e => { console.error(e); process.exit(1); });
