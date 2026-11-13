# Stories of the Prophets, Book One (ebook and print files)

The finished files are in `dist/`. `LISTING.md` says which file goes to which store and has the listing text.

## Rebuild after changes

1. Edit `config.json` (author, publisher, ISBN, year).
2. Run `node ebook/build.js` from the repository root. It needs Node and Playwright with Chromium.

- The story text and the illustrations live in `../islamic-kids-storybook.html` (`PAGES`, `QUIZ`, `SC`). The build reads them from there, so the web version and the book always match.
- `book.js` holds the page designs: frames, arches, chapter medallions, covers.
- `book.css` holds the typography.

The build fits text automatically: if a story page is too full, it makes the picture shorter, then the font smaller. It prints a warning if anything still overflows.
