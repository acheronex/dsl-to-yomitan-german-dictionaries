# German Language Support for Yomitan

This folder contains files to enable German word deinflection in Yomitan.

## Files

- `german-transforms.js` — German word deinflection rules for Yomitan

## What is this?

By default, Yomitan searches for exact dictionary matches. For German, this means if you have a dictionary entry for "laufen" but you look up "lief" or "gelaufen", Yomitan won't find it.

This file adds German deinflection rules that convert inflected German words back to their dictionary forms:
- **Verbs**: "lief" → "laufen", "gelaufen" → "laufen", "zu lesen" → "lesen"
- **Nouns**: "Männer" → "Mann", "Tische" → "Tisch"  
- **Adjectives**: "schnellste" → "schnell", "kältesten" → "kalt"
- **Umlauts**: "häufig" → "haeufig", "Bäume" → "Baume"

## Installation

### Method 1: Manual (Recommended)

1. Find your Yomitan extension folder:
   - **Chrome**: `chrome-extension_[ID]/js/language/de/`
   - **Firefox**: `moz-extension_[ID]/js/language/de/`
   
   To find the ID, open Yomitan settings in your browser and look at the URL, or search for `german-transforms.js` in your extensions folder.

2. Backup the original `german-transforms.js` file (if it exists)

3. Copy our `german-transforms.js` to the `js/language/de/` folder

4. Reload Yomitan

### Method 2: UserCSS (Alternative)

If you don't want to modify extension files, you can also try using Yomitan's built-in search matching options in settings.

## Current Limitations

This is a community-made solution and may not cover all German word forms. Known limitations:

- Not all irregular verb forms are covered
- Some edge cases may not work
- Umlaut handling is basic (ä→a, ö→o, ü→u)

Feel free to improve this file and contribute back!

## Credits

Original file created with assistance from AI. Improvements welcome!
