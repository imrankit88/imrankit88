# Selling guide: Stories of the Prophets, Book One

## Which file goes where

| Platform | Format | Upload these files |
|---|---|---|
| Amazon KDP, paperback | 8.5 × 8.5 in, premium colour, bleed, glossy cover | `…-print-interior.pdf` (manuscript) and `…-print-cover.pdf` (cover). Settings are in `print-specs.txt`. |
| Amazon Kindle eBook | Fixed-layout kids' book | Open `…-ebook.pdf` in Amazon's free **Kindle Kids' Book Creator** and export a `.kpf` file, then upload it to KDP. KDP also takes the EPUB. |
| Apple Books | Fixed-layout EPUB 3 | `…-fixed-layout.epub`, with `…-front-cover.jpg` as the cover |
| Google Play Books | EPUB or PDF | `…-fixed-layout.epub` (or `…-ebook.pdf`), with `…-front-cover.jpg` |
| Kobo Writing Life | EPUB | `…-fixed-layout.epub` |
| Gumroad, Payhip, Etsy (digital download) | PDF | `…-ebook.pdf` as the product file. Use `…-front-cover.jpg` and screenshots from `…-preview-sheet.png` as listing images. |
| Lulu, IngramSpark (print) | PDF | `…-print-interior.pdf`. Make the cover from their own template, because their spine width is different. Change `paperThicknessIn` in `config.json` and rebuild. |

## Before you publish

1. Put your real author name and publisher name in `ebook/config.json`, then run `node ebook/build.js`.
2. Have a scholar or teacher you trust check the text.
3. ISBN: KDP gives you a free ISBN for the paperback. If you use one, add it to `config.json` and rebuild. Amazon and Google ebooks don't need an ISBN. Apple and Kobo don't require one either.
4. Order one printed proof copy from KDP before you make the paperback live.
5. Apple checks EPUB files when you upload them. To test first, use EPUBCheck (free, from the W3C).

## Listing text (copy and paste)

**Title:** Stories of the Prophets
**Subtitle:** From Adam to Ibrahim – Islamic Stories from the Qur'an for Kids Ages 5–10
**Series:** Stories of the Prophets, Book 1
**Reading age:** 5–10 years (grades K–5)

**Description**

> Long ago, Allah sent prophets to teach people to worship Him alone and to be kind and good.
>
> This illustrated picture book tells six true stories from the Qur'an in simple, gentle words for young Muslim children: **Prophet Adam, Idris, Nuh, Hud, Salih and Ibrahim** (peace be upon them).
>
> Children travel from the beautiful garden of Jannah to the great ark of Nuh, from the giant pillars of 'Ad to the camel that came out of a rock, and to the fire that turned cool and safe for Ibrahim.
>
> **Inside you will find:**
> - Six chapters with Islamic geometric art on every page
> - Short ayahs in Arabic with easy English meanings
> - A "What We Learn" page after each story: saying sorry, loving to learn, patience, being thankful, keeping promises and courage
> - A "Talk Together" question for parents and teachers after each story
> - A story quiz, a good-manners star chart and a "This book belongs to" page
>
> Out of love and respect, no prophet is ever shown. Real photographs and gentle illustrations show the world around each story instead.
>
> It's a good fit for bedtime reading, weekend Islamic school, homeschooling, Ramadan and Eid gifts.

**Keywords (KDP allows 7):**
1. islamic books for kids
2. stories of the prophets for children
3. quran stories for kids
4. muslim children picture book
5. prophet stories ramadan gift
6. islamic bedtime stories ages 5-10
7. eid gift books for muslim kids

**Categories to pick:** Juvenile Nonfiction › Religious › Islamic · Juvenile Nonfiction › Religion › Islam · Juvenile Fiction › Religious › Islamic (pick whichever names the store shows)

## What's in the book

- Interior: 44 pages (title, "belongs to" page, copyright, Bismillah, parents' note, contents, 6 chapters, quiz, star chart, The End)
- Ebook: 46 pages (front cover and back cover added)
- Fonts: Baloo 2, Nunito, Amiri and Aref Ruqaa, all under the SIL Open Font License, so you can sell the book with them embedded
- Pictures: 13 pages use real photographs from Wikimedia Commons (no people's faces). All are free to use in a book you sell (CC0, public domain, CC BY or CC BY-SA). The photographers are credited on the copyright page, as these licences require, and the list is in `photos/credits.json`. Keep those credits in every edition.
- The other pages use original vector art made for this book. You own it along with the text.
