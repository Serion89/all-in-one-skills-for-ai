---
name: internationalization
description: Build software that works across languages, locales, and writing directions - externalize strings with ICU MessageFormat, handle plurals with CLDR categories, format dates, numbers, and currency with Intl, store time in UTC, design for text expansion and right-to-left layouts with logical CSS properties, and test with pseudo-localization. Use when adding a second language, building a multi-region product, or reviewing UI code for hard-coded text, formatting, or layout assumptions.
license: MIT
metadata:
  author: Serion89
  version: "1.0.0"
---

# Internationalization

Internationalization (i18n) is the engineering work that makes localization (l10n)
possible. Get the structure right once, and translators and locale data do the rest.
Retrofitting i18n into a finished UI is far more expensive than building it in.

## 1. Externalize every user-facing string

- No user-visible text in components, templates, or error responses that bypass the message catalog.
- Never build sentences by concatenating fragments. Word order differs by language:

```
// Wrong: "You have " + count + " new messages"
// Right: "You have {count, plural, one {# new message} other {# new messages}}"
```

- Use named placeholders, not positional ones, so translators can reorder them.
- Give each message a stable, descriptive key and a comment for translators explaining context (for example, whether "Post" is a noun or a verb).
- Use the framework's i18n library (for example, `react-intl`, `i18next`, `gettext`, Django i18n, Flutter `intl`) rather than a home-made lookup.

## 2. Plurals and gender

- Use CLDR plural categories through ICU MessageFormat: `zero`, `one`, `two`, `few`, `many`, `other`. English has two; Arabic has six; Polish has four.
- Never write `count === 1 ? "item" : "items"`. That rule is wrong for most languages.
- For grammatical gender, provide a message variant per gender value rather than assuming a default.

## 3. Dates, times, numbers, currency

- Store and transmit instants in UTC (ISO 8601 with `Z`). Convert to the user's time zone only at display time.
- Format with `Intl.DateTimeFormat`, `Intl.NumberFormat`, or the platform's equivalent. Do not hand-write date patterns.
- Specify the time zone explicitly when formatting. A date-only value (a birthday) must not be converted through a time zone.
- Store money as integer minor units with an ISO 4217 currency code. Format with `Intl.NumberFormat` using `style: "currency"`.
- Never assume a decimal separator, digit grouping, or the first day of the week.

## 4. Text, names, and input

- Do not assume "first name + last name", a fixed number of address lines, or a particular postal code format.
- Use `Intl.Collator` for sorting; `a.localeCompare(b)` without a locale is not reliable across languages.
- Count characters by grapheme cluster, not by `.length`. Emoji and combining marks break naive counts.
- Normalize Unicode input (NFC) before comparing or storing it, so visually identical strings compare equal.
- Do not uppercase or lowercase without a locale for user-visible text (Turkish dotted and dotless i).

## 5. Layout and right-to-left

- Set `dir` and `lang` on the root element from the active locale.
- Use **logical CSS properties**: `margin-inline-start` instead of `margin-left`, `padding-block` instead of `padding-top` and `padding-bottom`, `inset-inline-end` instead of `right`. The layout then mirrors automatically.
- Mirror only directional icons (arrows, back buttons, progress). Do not mirror logos, clocks, or media playback icons.
- Allow for text expansion: German and Finnish commonly run 30 to 50 percent longer than English. Do not fix widths on labels or buttons; test with the longest translation.
- Do not put text inside images. If unavoidable, provide localized variants.

## 6. Fallbacks and loading

- Define a fallback chain (for example, `pt-BR` -> `pt` -> `en`) and log missing keys so gaps are visible.
- Load only the active locale's catalog, not all of them, to keep bundles small.
- Keep the fallback language complete; a missing key should show readable text, never the raw key.

## 7. Testing

- **Pseudo-localization**: run the UI with accented, lengthened strings (for example, `[!!! Ŕéálíźéď ~~~~ !!!]`) to find hard-coded strings and truncation.
- **RTL check**: switch to an RTL locale or force `dir="rtl"` and review every screen.
- **Lint for literals**: add a lint rule that flags string literals in JSX or templates outside the catalog.
- **Locale matrix tests**: test date, number, and plural formatting for at least one language with plural categories beyond `one` and `other`, and one time zone with a half-hour offset.

## Checklist

- [ ] No user-visible hard-coded strings; every message is keyed and commented.
- [ ] No sentence concatenation; placeholders are named.
- [ ] Plurals use CLDR categories.
- [ ] Times stored in UTC; formatting uses `Intl` with an explicit zone.
- [ ] Money is integer minor units with a currency code.
- [ ] Layout uses logical properties; tested with pseudo-localization and RTL.

## Anti-patterns

- `"Hello, " + name + "!"` in code.
- Formatting dates with `MM/DD/YYYY` string templates.
- Storing a localized display string in the database as the source of truth.
- Fixed-width buttons sized for English labels.
- Using a language code as a locale (`"en"` for a US-English-only product, or `"zh"` without a script or region when it matters).
