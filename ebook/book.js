/* Builds the printed/ebook pages in the browser. Uses the scenes (SC) and story text (CH, PAGES, QUIZ, VALUES)
   extracted from ../islamic-kids-storybook.html by build.js. No prophet or person is ever drawn. */
(function () {
  const CFG = window.CFG;
  const NUM = ['One', 'Two', 'Three', 'Four', 'Five', 'Six'];
  const DARK = { adam: '#1D5A3C', idris: '#27367A', nuh: '#134C7A', hud: '#7A4718', salih: '#7C3322', ibrahim: '#682043' };
  const NAVY = '#0B1F45', TEAL = '#0F5257';

  function pts(cx, cy, R, r, n, rot) {
    const p = [];
    for (let i = 0; i < 2 * n; i++) { const a = (rot + i * 180 / n) * Math.PI / 180, rr = i % 2 ? r : R; p.push((cx + Math.cos(a) * rr).toFixed(2) + ',' + (cy + Math.sin(a) * rr).toFixed(2)); }
    return p.join(' ');
  }
  const corners = (s, col) => [[0, 0], [s, 0], [0, s], [s, s]].map(([x, y]) => `<polygon points="${pts(x, y, 9, 3.5, 4, 0)}" fill="${col}"/>`).join('');

  const DEFS = `<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F8E09A"/><stop offset=".45" stop-color="#CF9A36"/><stop offset=".72" stop-color="#F4D47F"/><stop offset="1" stop-color="#B9832A"/></linearGradient>
  <pattern id="pat-lines" width="64" height="64" patternUnits="userSpaceOnUse"><polygon points="${pts(32, 32, 32, 24.5, 8, 0)}" fill="none" stroke="#E2B65A" stroke-width="1.4"/><circle cx="32" cy="32" r="7" fill="none" stroke="#E2B65A" stroke-width="1.2"/>${corners(64, '#E2B65A')}</pattern>
  <pattern id="pat-paper" width="64" height="64" patternUnits="userSpaceOnUse"><polygon points="${pts(32, 32, 32, 24.5, 8, 0)}" fill="none" stroke="#E7D8B6" stroke-width="1"/><circle cx="32" cy="32" r="7" fill="none" stroke="#E7D8B6" stroke-width="1"/>${corners(64, '#EADDC0')}</pattern>
  <pattern id="pat-stars" width="26" height="26" patternUnits="userSpaceOnUse"><polygon points="${pts(13, 13, 8.5, 6.5, 8, 0)}" fill="#E9C46A"/><circle cx="13" cy="13" r="2.3" fill="#7A5418"/></pattern>
  <pattern id="pat-tile" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" fill="${TEAL}"/><polygon points="${pts(16, 16, 15, 11.5, 8, 0)}" fill="none" stroke="#E2B65A" stroke-width="1.1"/><circle cx="16" cy="16" r="3.2" fill="#E2B65A"/></pattern>
  </defs></svg>`;
  document.body.insertAdjacentHTML('afterbegin', DEFS);

  /* ---------- ornaments ---------- */
  function rosette(cx, cy, r, fill) {
    let p = '';
    for (let i = 0; i < 8; i++) p += `<ellipse cx="0" cy="${-r * .56}" rx="${r * .22}" ry="${r * .42}" transform="rotate(${i * 45})" fill="url(#gold)"/>`;
    return `<g transform="translate(${cx} ${cy})"><circle r="${r}" fill="${fill}" stroke="url(#gold)" stroke-width="2.5"/>${p}<circle r="${r * .26}" fill="#FBF5E8" stroke="#C8922E" stroke-width="1.5"/></g>`;
  }
  function frame(band, num) {
    const o = 24, b = 50, e = 816;
    const ring = `M${o},${o} H${e - o} V${e - o} H${o}Z M${b},${b} V${e - b} H${e - b} V${b}Z`;
    return `<svg class="frame" viewBox="0 0 816 816" aria-hidden="true">
    <path d="${ring}" fill="${band}" fill-rule="evenodd"/><path d="${ring}" fill="url(#pat-stars)" fill-rule="evenodd" opacity=".9"/>
    <rect x="${o}" y="${o}" width="${e - 2 * o}" height="${e - 2 * o}" fill="none" stroke="url(#gold)" stroke-width="3"/>
    <rect x="${b}" y="${b}" width="${e - 2 * b}" height="${e - 2 * b}" fill="none" stroke="url(#gold)" stroke-width="3"/>
    <rect x="${b + 7}" y="${b + 7}" width="${e - 2 * b - 14}" height="${e - 2 * b - 14}" fill="none" stroke="#C8922E" stroke-width="1"/>
    ${[[37, 37], [779, 37], [37, 779], [779, 779]].map(([x, y]) => rosette(x, y, 25, band.startsWith('rgba') ? NAVY : band)).join('')}
    ${num ? `<circle cx="408" cy="779" r="20" fill="#FBF5E8" stroke="url(#gold)" stroke-width="3"/><text x="408" y="785.5" text-anchor="middle" font-family="Baloo 2" font-weight="800" font-size="17" fill="#1C3B73">${num}</text>` : ''}
    </svg>`;
  }
  function divider(w = 260, col = '#C8922E') {
    return `<svg class="dv" width="${w}" height="22" viewBox="0 0 ${w} 22" aria-hidden="true"><line x1="0" y1="11" x2="${w / 2 - 40}" y2="11" stroke="${col}" stroke-width="1.5"/><line x1="${w / 2 + 40}" y1="11" x2="${w}" y2="11" stroke="${col}" stroke-width="1.5"/>
    <polygon points="${pts(w / 2, 11, 10, 7.65, 8, 0)}" fill="${col}"/><circle cx="${w / 2 - 28}" cy="11" r="3" fill="${col}"/><circle cx="${w / 2 + 28}" cy="11" r="3" fill="${col}"/></svg>`;
  }
  function arch(x0, y0, w, h, a) {
    const x1 = x0 + w, y1 = y0 + h, m = x0 + w / 2;
    return `M${x0},${y1} L${x0},${y0 + a} C${x0},${y0 + a * .42} ${x0 + w * .28},${y0 + a * .1} ${m},${y0} C${x0 + w * .72},${y0 + a * .1} ${x1},${y0 + a * .42} ${x1},${y0 + a} L${x1},${y1}Z`;
  }
  function archArt(scene, W, H, alt) {
    const id = 'ac' + (uid++), i = 12, a = Math.min(W * .26, H * .45);
    const inner = arch(i, i + 6, W - 2 * i, H - i - 6, a - 8), outer = arch(0, 0, W, H, a);
    return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${alt.replace(/"/g, '')}">
    <clipPath id="${id}"><path d="${inner}"/></clipPath><path d="${outer}" fill="url(#pat-tile)"/>
    <g clip-path="url(#${id})">${CFG.photos[scene] ? `<image href="${CFG.photos[scene]}" x="${i}" y="${i + 6}" width="${W - 2 * i}" height="${H - i - 6}" preserveAspectRatio="xMidYMid slice"/>` : `<svg x="${i}" y="${i + 6}" width="${W - 2 * i}" height="${H - i - 6}" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice">${SC[scene]()}</svg>`}</g>
    <path d="${inner}" fill="none" stroke="url(#gold)" stroke-width="4"/><path d="${outer}" fill="none" stroke="url(#gold)" stroke-width="3"/></svg>`;
  }
  function shamsa(fill) {
    let p = '';
    for (let i = 0; i < 32; i++) p += `<path d="M0,-216 Q12,-197 0,-176 Q-12,-197 0,-216Z" transform="rotate(${i * 11.25})" fill="url(#gold)"/>`;
    return `<svg class="shamsa" viewBox="-220 -220 440 440" aria-hidden="true">${p}<circle r="178" fill="${fill}" stroke="url(#gold)" stroke-width="4"/><circle r="166" fill="none" stroke="#E2B65A" stroke-width="1.2"/>
    <polygon points="${pts(0, 0, 160, 122.5, 8, 0)}" fill="none" stroke="#E2B65A" stroke-width="1" opacity=".45"/><polygon points="${pts(0, 0, 160, 122.5, 8, 22.5)}" fill="none" stroke="#E2B65A" stroke-width="1" opacity=".45"/></svg>`;
  }
  const badgeSVG = () => `<svg viewBox="0 0 108 108" aria-hidden="true"><polygon points="${pts(54, 54, 54, 41.3, 8, 22.5)}" fill="url(#gold)" stroke="#8C6020" stroke-width="1.5"/><circle cx="54" cy="54" r="36" fill="#FFF3D0" stroke="#B9832A" stroke-width="2"/></svg>`;
  const ribbon = () => `<svg viewBox="0 0 540 78" aria-hidden="true"><path d="M0,39 Q22,6 60,4 H480 Q518,6 540,39 Q518,72 480,74 H60 Q22,72 0,39Z" fill="url(#gold)" stroke="#8C6020" stroke-width="1.5"/><path d="M0,39 Q22,6 60,4 H480 Q518,6 540,39 Q518,72 480,74 H60 Q22,72 0,39Z" fill="none" stroke="#8C6020" stroke-width="1" transform="translate(270 39) scale(.95 .8) translate(-270 -39)"/></svg>`;
  const CART = 'M0,105 Q40,20 110,12 H510 Q580,20 620,105 Q580,190 510,198 H110 Q40,190 0,105Z';
  const cart = () => `<svg viewBox="0 0 620 210" preserveAspectRatio="none" aria-hidden="true"><path d="${CART}" fill="#0A1A3A" stroke="url(#gold)" stroke-width="3.5"/><path d="${CART}" fill="none" stroke="#E2B65A" stroke-width="1.2" transform="translate(310 105) scale(.95 .86) translate(-310 -105)"/></svg>`;
  const TALK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h18v12H9l-6 5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="8" cy="10" r="1.2" fill="currentColor"/><circle cx="12" cy="10" r="1.2" fill="currentColor"/><circle cx="16" cy="10" r="1.2" fill="currentColor"/></svg>';
  const ayah = a => `<div class="ayah"><div class="ar" lang="ar">${a.ar}</div><div class="en">${a.en}</div><div class="ref">${a.ref}</div></div>`;

  /* ---------- page specs ---------- */
  function frontHTML() {
    return `<div class="glowbg"></div>${frame(NAVY)}<div class="cv-ar" lang="ar">قصص الأنبياء</div><div class="cv-title">${CFG.title}</div><div class="cv-glow"></div>
    <div class="cv-art">${archArt('cover', 440, 400, 'A starry desert night with a crescent moon, a lantern and a camel caravan')}</div>
    <div class="cv-badge" style="left:110px;top:528px">${badgeSVG()}<span>${CFG.series.replace(' ', '<br>')}</span></div>
    <div class="cv-badge" style="left:598px;top:528px">${badgeSVG()}<span>Ages<br>5–10</span></div>
    <div class="cv-rib">${ribbon()}<div class="t">${CFG.subtitle}</div></div><div class="cv-author">${CFG.author}</div>`;
  }
  function backHTML() {
    return `<div class="glowbg"></div>${frame(NAVY)}<div class="bk"><div class="ar" lang="ar">قصص الأنبياء</div><h2>Six true stories from the Qur’an</h2>${divider(240, '#E2B65A')}
    <p>Long ago, Allah sent prophets to teach people to worship Him alone and to be kind and good. Travel from the beautiful garden of Jannah to the great ark of Nuh, from the giant pillars of ‘Ad to the camel that came out of a rock, and to the fire that turned cool for Ibrahim.</p>
    <ul><li>Simple words for children aged 5 to 10</li><li>Short ayahs in Arabic with easy meanings</li><li>A lesson and a talk-together question after every story</li><li>A story quiz and a good-manners star chart</li></ul>
    <div class="meds">${VALUES.map(k => `<div class="med" lang="ar">${CH[k].ar}</div>`).join('')}</div>
    <p class="note">Out of love and respect, no prophet is ever drawn in this book.</p></div>
    <div class="bk-foot">${CFG.publisher}<br>Ages 5–10</div>`;
  }
  const S = {
    front: () => ({ cls: 'night cover', frameless: true, html: frontHTML(), alt: `${CFG.title}: ${CFG.subtitle}. Front cover.` }),
    back: () => ({ cls: 'night cover', frameless: true, html: backHTML(), alt: 'Back cover' }),
    title: () => ({ cls: 'paper', html: `<div class="content"><div class="ar-big" lang="ar">قصص الأنبياء</div>${divider()}<h1>${CFG.title}</h1><div class="series">${CFG.series}</div><div class="subt">${CFG.subtitle}</div>
      <div>${archArt('end', 300, 220, 'Lanterns glowing under a crescent moon')}</div><div class="author">Written by ${CFG.author}</div></div>` }),
    belongs: () => ({ cls: 'paper', html: `<div class="content">${archArt('intro', 320, 270, 'Glowing lanterns over a green star pattern')}<div class="bl">This book belongs to</div><div class="nameline"></div><div class="hint">Write your name on the line</div><div class="bl-ar" lang="ar">هٰذَا الْكِتَابُ مِلْكُ</div></div>` }),
    copy: () => ({ cls: 'paper', html: `<div class="prose copy"><div class="bt">${CFG.title}, ${CFG.series}: ${CFG.subtitle}</div>
      <p>Text and illustrations © ${CFG.year} ${CFG.author}. All rights reserved.</p>
      <p>No part of this book may be copied, stored or shared in any form without written permission from the publisher, except for short quotations in reviews.</p>
      ${CFG.isbn ? `<p>ISBN: ${CFG.isbn}</p>` : ''}
      <p>The Qur’anic verses are shown in Arabic. The English meanings are simplified for young readers and are not a full translation. For study, please use a complete translation and learn from a qualified teacher.</p>
      <p>Out of love and respect, no prophet is drawn in this book.</p>
      ${Object.keys(CFG.credits).length ? `<p>Photo credits: ${Object.values(CFG.credits).join('; ')}.</p>` : ''}
      <p>Published by ${CFG.publisher}. First edition ${CFG.year}.</p></div>` }),
    bismillah: () => ({ cls: 'night', band: NAVY, pre: '<div class="glowbg"></div>', html: `<div class="content"><div class="cart">${cart()}<div class="t" lang="ar">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div></div><p class="cream">In the name of Allah, the Most Gracious, the Most Merciful</p>${divider(240, '#E2B65A')}</div>` }),
    parents: () => ({ cls: 'paper', num: true, html: `<div class="prose"><h2>For Parents and Teachers</h2>${divider(200)}
      <p>This book tells six stories from the Qur’an, from Prophet Adam to Prophet Ibrahim, peace be upon them, in simple words for children aged 5 to 10.</p>
      <p>Out of love and respect, no prophet is drawn in this book. The pictures show the world around each story instead.</p>
      <p>Each story ends with a lesson and a question to talk about together. Short ayahs are shown in Arabic with a simple English meaning. A few details come from the tradition of tafsir; these are marked “It is said” or “Many scholars say”.</p>
      <p>When you read a prophet’s name, help your child say <b>‘alayhis-salam</b>: peace be upon him.</p></div>` }),
    toc: () => ({ cls: 'paper', num: true, toc: true, html: '' }),
    quiz: () => ({ cls: 'paper', num: true, html: `<div class="content" style="justify-content:space-between"><div><h1 style="font-size:42px">Story Quiz</h1><div class="hint" style="font-style:normal;font-size:18px">Colour in the circle next to the right answer!</div></div>
      <div class="quiz">${QUIZ.map((q, i) => `<div class="q"><b>${i + 1}. ${q[0]}</b><div class="o">${q[1].map(o => `<span>${o}</span>`).join('')}</div></div>`).join('')}</div>
      <div class="answers">Answers: ${QUIZ.map((q, i) => `${i + 1}. ${q[1][q[2]]}`).join(' · ')}</div></div>` }),
    stars: () => ({ cls: 'paper', num: true, html: `<div class="content"><h1 style="font-size:42px">My Good Manners Stars</h1><div class="hint" style="font-style:normal;font-size:18px">Colour in a star each time you practise a good manner.</div>${divider()}
      <div class="stars">${VALUES.map(k => `<div class="s"><svg viewBox="0 0 128 128"><polygon points="${pts(64, 64, 60, 46, 8, 22.5)}" fill="#FFFDF7" stroke="${CH[k].color}" stroke-width="4"/><circle cx="64" cy="64" r="30" fill="none" stroke="${CH[k].color}" stroke-width="2" stroke-dasharray="4 5"/></svg><small>Prophet ${CH[k].name}</small><b>${CH[k].value}</b></div>`).join('')}</div></div>` }),
    end: () => ({ cls: 'night', band: NAVY, pre: '<div class="glowbg"></div>', html: `<div class="content"><div class="ar-big gold" lang="ar">الحمد لله</div><h1>The End</h1>${divider(240, '#E2B65A')}
      <div class="cart small">${cart()}<div class="t" lang="ar">رَّبِّ زِدْنِي عِلْمًا</div></div><p class="cream">“My Lord, increase me in knowledge.”<br>Surah Ta-Ha 20:114</p></div>` }),
  };
  function opener(ch) {
    const c = CH[ch];
    return { cls: 'opener', ch, band: 'rgba(0,0,0,.3)', chapter: ch, alt: `Chapter ${c.n}: Prophet ${c.name}, ${c.alt}`,
      html: `<div class="op-top">Chapter ${NUM[c.n - 1]}</div>${shamsa(DARK[ch])}<div class="op-ar" lang="ar"><span>${c.ar}</span></div><div class="op-pbuh" lang="ar">عليه السلام</div><div class="op-name">Prophet ${c.name}</div><div class="op-sub">${c.alt}</div>` };
  }
  function story(p, first) {
    const c = CH[p.ch]; let body = '';
    p.body.forEach((t, i) => { body += `<p>${t}</p>`; if (p.ayah && (p.ayah.after ?? p.body.length - 1) === i) body += ayah(p.ayah); });
    return { cls: 'paper story' + (first ? ' first' : ''), ch: p.ch, band: DARK[p.ch], num: true, scene: p.scene, alt: p.alt,
      html: `<div class="art"></div><div class="txt"><div class="eyebrow">Prophet ${c.name} <span class="pbuh" lang="ar">عليه السلام</span></div><h2>${p.title}</h2>${body}</div>` };
  }
  function lesson(p) {
    const c = CH[p.ch];
    return { cls: 'paper', ch: p.ch, band: DARK[p.ch], num: true, html: `<div class="ls"><div class="ls-h">What We Learn</div>${divider(220)}
      <div class="badge"><svg viewBox="0 0 226 226" aria-hidden="true"><polygon points="${pts(113, 113, 110, 84, 8, 22.5)}" fill="${c.color}" stroke="url(#gold)" stroke-width="5"/><circle cx="113" cy="113" r="70" fill="#FFFBF0" stroke="url(#gold)" stroke-width="4"/></svg>
      <div class="bt"><small>Good manner</small><b>${c.value}</b></div></div>
      <p class="ls-t">${p.lesson}</p><div class="talk" style="color:${DARK[p.ch]}">${TALK}<div style="color:#2A2320"><b>Talk together</b><br>${p.talk}</div></div></div>` };
  }
  function specs(mode) {
    const L = [];
    if (mode === 'ebook') L.push(S.front());
    L.push(S.title(), S.belongs(), S.copy(), S.bismillah(), S.parents(), S.toc());
    VALUES.forEach(ch => { L.push(opener(ch)); const ps = PAGES.filter(p => p.ch === ch); ps.forEach((p, i) => L.push(story(p, i === 0))); L.push(lesson(ps.find(p => p.lesson))); });
    const q = S.quiz(); q.label = 'Story Quiz'; L.push(q);
    const st = S.stars(); st.label = 'My Good Manners Stars'; L.push(st);
    L.push(S.end());
    if (mode === 'ebook') L.push(S.back());
    return L;
  }
  function tocHTML(L) {
    const row = (c, mark, name, ar, sm, pg) => `<li style="--c:${c}"><span class="n">${mark}</span><span>${name}${ar ? `<span class="ar" lang="ar">${ar}</span>` : ''}${sm ? `<span class="sm">${sm}</span>` : ''}</span><span class="dots"></span><span class="pg">${pg}</span></li>`;
    const star = `<svg viewBox="-10 -10 20 20" width="18" height="18"><polygon points="${pts(0, 0, 9, 6.9, 8, 0)}" fill="#F2CF7A"/></svg>`;
    let rows = VALUES.map(k => { const sp = L.find(s => s.chapter === k), c = CH[k]; return row(c.color, c.n, `Prophet ${c.name}`, c.ar, c.alt, sp.n); }).join('');
    rows += L.filter(s => s.label).map(s => row('#0F5257', star, s.label, '', '', s.n)).join('');
    return `<div class="content"><h1 style="font-size:44px">Contents</h1>${divider()}<ul class="toc">${rows}</ul></div>`;
  }

  /* ---------- DOM + fitting ---------- */
  function pageEl(sp, mode) {
    const s = document.createElement('section'); s.className = 'page ' + sp.cls;
    if (sp.ch) { s.style.setProperty('--ch', CH[sp.ch].color); s.style.setProperty('--dk', DARK[sp.ch]); }
    const bg = sp.cls.includes('paper') ? '<svg class="bg" aria-hidden="true"><rect width="100%" height="100%" fill="url(#pat-paper)"/></svg>'
      : `<svg class="bg" aria-hidden="true"><rect width="100%" height="100%" fill="url(#pat-lines)" opacity="${sp.cls.includes('opener') ? .2 : .14}"/></svg>`;
    s.innerHTML = bg + `<div class="trim">${sp.pre || ''}${sp.frameless ? '' : frame(sp.band || TEAL, sp.num ? sp.n : null)}${sp.html}</div>`;
    if (mode === 'print') { s.style.setProperty('--tx', (sp.n % 2 === 1 ? 0 : 12) + 'px'); s.style.setProperty('--ty', '12px'); }
    return s;
  }
  async function fontsReady() {
    const f = ['400 20px Amiri', '700 20px Amiri', '700 20px "Aref Ruqaa"', '800 20px "Baloo 2"', '700 20px "Baloo 2"', '400 20px Nunito', 'italic 400 20px Nunito', '700 20px Nunito', '800 20px Nunito'];
    await Promise.all(f.map(x => document.fonts.load(x, 'Abc بسم الله')));
    await document.fonts.ready;
  }
  function fitStory(el, sp) {
    const art = el.querySelector('.art'), txt = el.querySelector('.txt');
    for (const fs of [19.5, 19, 18.5, 18, 17.5, 17, 16.5, 16, 15.5, 15]) for (const H of [400, 380, 360, 340, 320]) {
      el.style.setProperty('--fs', fs + 'px'); el.style.setProperty('--H', H + 'px');
      if (art.dataset.h != H) { art.innerHTML = archArt(sp.scene, 632, H, sp.alt); art.dataset.h = H; }
      if (txt.scrollHeight <= txt.clientHeight + 1) return;
    }
  }
  function setSize(w, h) {
    document.documentElement.style.setProperty('--pw', w + 'px'); document.documentElement.style.setProperty('--ph', h + 'px');
    document.getElementById('pagesize').textContent = `@page{size:${w}px ${h}px;margin:0}`;
  }
  function overflowWarnings() {
    const w = [];
    document.querySelectorAll('.page').forEach((p, i) => p.querySelectorAll('.txt,.content,.prose,.ls,.bk').forEach(b => { if (b.scrollHeight > b.clientHeight + 2) w.push(`page ${i + 1}: ${b.className} overflows by ${b.scrollHeight - b.clientHeight}px`); }));
    return w;
  }

  async function build(mode) {
    const book = document.getElementById('book'); book.innerHTML = ''; book.className = mode === 'sheet' ? 'sheet' : '';
    const print = mode === 'print', bleed = print ? 12 : 0;
    const pw = 816 + (print ? 12 : 0), ph = 816 + 2 * bleed; setSize(pw, ph);
    if (mode === 'front') { book.append(pageEl(S.front(), mode)); await fontsReady(); return { w: pw, h: ph, count: 1 }; }
    const L = specs(mode === 'sheet' ? 'ebook' : mode), off = (mode === 'print') ? 0 : 1;
    L.forEach((sp, i) => sp.n = i - off + 1);
    L.forEach(sp => { if (sp.toc) sp.html = tocHTML(L); });
    L.forEach(sp => { sp.el = pageEl(sp, mode); book.append(sp.el); });
    await fontsReady();
    L.forEach(sp => {
      if (sp.scene) fitStory(sp.el, sp);
      const ar = sp.el.querySelector('.op-ar span'); if (ar) { let fs = 92; while (ar.offsetWidth > 370 && fs > 50) { fs -= 4; ar.style.fontSize = fs + 'px'; } }
    });
    await fontsReady();
    const nav = L.map((sp, i) => ({ i, chapter: sp.chapter, label: sp.label })).filter(x => x.chapter || x.label)
      .map(x => ({ i: x.i, label: x.chapter ? `Chapter ${CH[x.chapter].n}: Prophet ${CH[x.chapter].name}` : x.label }));
    const alts = L.map(sp => (sp.alt ? sp.alt + '. ' : '') + sp.el.querySelector('.trim').innerText.replace(/\s+/g, ' ').trim());
    return { w: pw, h: ph, count: L.length, warn: overflowWarnings(), nav, alts };
  }
  async function buildWrap(spinePx) {
    const b = 12, W = Math.round(2 * b + 816 * 2 + spinePx), H = 816 + 2 * b; setSize(W, H);
    const book = document.getElementById('book'); book.className = ''; book.innerHTML = '';
    const s = document.createElement('section'); s.className = 'page night';
    s.innerHTML = `<svg class="bg" aria-hidden="true"><rect width="100%" height="100%" fill="url(#pat-lines)" opacity=".14"/></svg>
      <div class="trim" style="left:${b}px;top:${b}px">${backHTML()}</div><div class="trim" style="left:${b + 816 + spinePx}px;top:${b}px">${frontHTML()}</div>`;
    book.append(s); await fontsReady();
    return { w: W, h: H, warn: overflowWarnings() };
  }
  window.BOOK = { build, buildWrap };
})();
