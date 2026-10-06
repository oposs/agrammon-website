# Port theme2 ("Wissenschaftliches Instrument") into the Hugo site

Date: 2026-10-06 · Status: approved design, pending spec review

## Goal

The customer chose design proposal **theme2** (static mockup in `static/theme2/`).
Make the real Hugo site (`/de/`, `/en/`, `/fr/`) look like theme2 on every page,
then remove the mockups.

**Unchanged:** all content and URLs, `{{< todo >}}` flags, relref links, the
image/link render hooks' existing behaviour, `OPEN-QUESTIONS.md`.

**Done when:**
- every page renders in the theme2 look, in all three languages;
- `hugo` builds with zero warnings;
- the site works at phone width (375 px) without horizontal scroll;
- all 36 download PDFs and all internal links still resolve;
- `static/theme2`, `static/theme3`, `static/designs` are deleted;
- the GitHub Pages preview can be shown to the customer as the real site.

## Decisions

| Topic | Decision |
|---|---|
| CSS stack | Plain CSS (theme2 is already custom-property CSS). **UIkit and Sass removed.** Hugo concatenates, minifies and fingerprints. |
| Dark mode | **Dropped.** Light only, as approved. Toggle and `theme.js` removed. |
| Homepage | Hero + the three model cards. The mockup's "Wie Agrammon rechnet" section is **not** ported. |
| Top navigation | Flat bar, mockup's five items: Dokumentation · Modell · Downloads · Kontakt · Über uns. No dropdowns. |
| Links page | Linked from the **footer** (with Kontakt), not the bar. |
| Mobile nav | Menu button in the bar opens the same items as a vertical list below it. Few lines of JS, `aria-expanded`, works without JS by falling back to the footer links. |
| Fonts | Space Grotesk, IBM Plex Sans, IBM Plex Mono **self-hosted** (woff2, latin + latin-ext) under `static/fonts/`. No request to Google. |
| New copy | **None.** Pages keep their current titles; mockup headlines/ledes (e.g. "Wer Ihnen weiterhilft") are not used. |
| Content format | Stays Markdown. Theme2 components come from CSS + layouts + render hooks, not from moving content into front matter. |

## Structure

```
layouts/
  _default/baseof.html      skeleton: fonts, one stylesheet, nav script
  _default/single.html      pagehead + prose
  _default/list.html        pagehead + prose + child list
  _default/_markup/render-link.html   (extended, see below)
  _default/_markup/render-image.html  (unchanged)
  partials/head.html        CSS pipeline, meta, favicon
  partials/header.html      pine bar: brand, menu, language switcher, menu button
  partials/footer.html      copyright line + Links + Kontakt
  partials/pagehead.html    eyebrow + title + breadcrumb (all pages except home)
  partials/section-nav.html sidebar tree of a section's pages (docs + downloads)
  partials/model-cards.html three variant cards (Modell page + home)
  index.html                hero + model cards
  dokumentation/{single,list}.html
  downloads/{single,list}.html
  modell/single.html
  kontakt/single.html
  ueber-uns/single.html
  404.html
  shortcodes/todo.html      (markup unchanged, restyled)
assets/css/
  base.css      tokens (:root), reset, typography, .wrap, .eyebrow, .btn, .prose, .todo
  chrome.css    header bar, language switcher, mobile menu, pagehead, crumb, footer
  home.css      hero, model cards (.variant)
  docs.css      .doc grid, .doc-nav sidebar
  downloads.css .dl-row, .dlnav tiles
  pages.css     kontakt cards, über-uns team blocks, links lists, modell usage
static/fonts/   self-hosted woff2 + fonts.css (@font-face)
```

Source for all CSS: `static/theme2/design-proposal.css`, split by the files
above. Mockup-only rules (`.demobadge`, `.flux*`, `.stat*`, `.how`, `.stage*`)
are not ported.

### Header

- Built from the existing per-language `menus.main` in `hugo.yaml`; the
  `home` and `links` entries are skipped in the bar. Active item = the
  current page's top-level section.
- Language switcher in theme2 style (`DE / EN / FR`, current in leaf green),
  same translation-aware URLs as today (`hugo.Sites` + `.AllTranslations`,
  fallback to the language root).
- Brand "Agrammon" links to the current language's home.

### Page header

`partials/pagehead.html`: eyebrow, `<h1>` = page title, breadcrumb on
sub-pages. Eyebrow defaults to the section's name via i18n
(Dokumentation / Downloads / Modell / …); an optional `eyebrow` front-matter
field overrides it. No new text otherwise.

### Sidebar tree (docs + downloads)

`partials/section-nav.html` takes the section, lists "Übersicht" (i18n)
plus its pages by weight, nested children (Modellparameter →
Emissionsfaktoren, Korrekturfaktoren) indented as `.sub`. Current page
gets `.active`. Sticky on desktop, static above the content below 860 px.
Replaces the current hard-coded sidebar in `dokumentation/single.html`.

## Content → theme2 components

### Downloads (Berichte, Weitere Informationen, Modell Agrammon, bLSmodelR)

Must stay **simple for the customer to edit**. Authoring format is today's,
unchanged — one Markdown bullet per document:

```markdown
- Titel des Berichts. Zusatzinfo (2022-06-15) — [Download](/assets/Documents/datei.pdf)
```

Adding a document = copying a line, changing text and file name, putting
the PDF into `static/assets/Documents/`. `##` headings group documents.

Rendering:
- `downloads/single.html` renders each list item as a `.dl-row`: text left,
  PDF button right. The layout removes the ` — ` separator before the link
  in the rendered HTML (`replaceRE`), so content files need no change.
- `render-link.html`: inside the Downloads section, links to `*.pdf` render
  as `<a class="dl">` with the i18n label `PDF ↓` (DE/EN/FR), regardless of
  the link text.
- `##` headings render as `.dl-group h2`.
- A short how-to comment block at the top of each Downloads content file
  (HTML comment, invisible on the site) shows the line format.

`downloads/list.html` (overview): the `_index` Markdown intro, then numbered
`.dlnav` tiles generated from the sub-pages: title + a computed document
count (number of PDF links on that page, i18n "{n} Dokumente / documents /
documents"). No new descriptive text, nothing extra to maintain.

### Links

`##` headings → group labels (`.linkgroup .h`), lists → `.linklist`.
`render-link.html` adds `↗` and the bare domain (`.u`) to external links in
list items on the Links page; external links elsewhere get `↗` only.

### Dokumentation

`.prose` styling, sidebar tree, figures and `{{< todo >}}` restyled to
theme2 (`.todo` amber box). No content changes.

### Modell

`partials/model-cards.html`: three `.variant` cards using the existing i18n
strings (`modell_einzel`, `modell_einzel_desc`, …) and the existing
`model.agrammon.ch/<variant>/?lang=<lang>` links; the cantonal card keeps
the "frozen · offline 2028" tag. Modell page: intro, cards, note, then the
Markdown body (Modellbedienung) in `.prose`; the manuals list renders as
`.dl-row`s (link text = title, `PDF ↓` badge).

### Kontakt

`kontakt/single.html` splits the rendered content at each `<h2>` and wraps
each block in a `.ccard` (heading → `.role` label). Content unchanged.

### Über uns

Existing front matter (organisations, people, `image:` page resources)
(`team_sections`, `steering*`, `supported*`) rendered as theme2
`.team-block`s: `.people` portraits (`Fill "200x200 webp q85"` as today),
the steering-group `.steer` list, and the "Unterstützt durch" block.

### Home

Hero: `_index` Markdown text, buttons "Modell starten →" (→ Modell page)
and "Dokumentation" (i18n), flux image per language
(`Stoffflussmodell-Agrammon-2015{d,e,f}.jpg`) with caption (i18n).
Below: `partials/model-cards.html`.

## Removed

- `assets/uikit/`, `assets/scss/`, `assets/js/theme.js`
- `layouts/partials/head.html` Sass/UIkit pipeline (rewritten)
- dark-mode i18n strings and markup
- `"github:sass/dart-sass"` from `mise.toml` (CI installs via mise-action,
  so the workflows need no change)
- `static/theme2/`, `static/theme3/`, `static/designs/` (last step, after
  the port is verified). `static/theme2/img/` team photos are duplicates of
  the page resources in `content/ueber-uns/` and go too.

## Verification

1. `mise exec -- hugo` — zero warnings, zero errors.
2. Link check over the built site: every internal `href`/`src` resolves;
   all 36 PDFs under `/assets/` are linked and exist.
3. Screenshots (Playwright) of each page type — home, docs single, docs
   list, downloads overview, Berichte, Modell, Kontakt, Über uns, Links,
   404 — at 1280 px and 375 px, in DE and FR; compare side by side with the
   matching mockup page.
4. Language switcher on each page type points to the right translation.
5. Mobile menu opens/closes by keyboard and mouse; no horizontal scroll at
   375 px.
6. Push → GitHub Pages build green → customer preview.

## Out of scope

- Any new or rewritten text (mockup headlines, "Wie Agrammon rechnet").
- Dark mode.
- Resolving `OPEN-QUESTIONS.md` items and the hosting decision.
