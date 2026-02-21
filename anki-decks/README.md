# Anki Deck for Yomitan German

A pre-configured Anki deck optimized for German vocabulary learning with Yomitan.

## Features

- **Proper fields** — expression, reading, meaning, sentence, audio, conjugation, frequencies
- **Custom styling** — red highlights for keywords, gray translation text
- **Ready to use** — import and connect to Yomitan immediately
- **Example cards** — test entries included

---

## Quick Setup / Быстрая настройка

### 1. Import Deck / Импорт колоды

Double-click `German Yomitan.apkg` to import into Anki.

### 2. Install Anki Add-ons / Установка дополнений

Install these add-ons in Anki:
- **AnkiConnect** — bridge between browser and Anki
- **AwesomeTTS** — text-to-speech
- **Google Translate** — quick translations

### 3. Configure Yomitan / Настройка Yomitan

1. In Yomitan settings, enable Anki integration
2. Go to **Configure Anki card format**
3. Select:
   - **Deck**: `Default`
   - **Model**: `Yomitan Close GERMAN`

### 4. Field Mapping / Сопоставление полей

| Field | Value |
| :--- | :--- |
| sentence | `{sentence}` |
| Sentence Furigana | `{sentence-furigana}` |
| Term | `{expression}` |
| Reading | `{reading}` |
| Meaning | `{glossary}` |
| audio | `{audio}` |
| Furigana | `{furigana}` |
| Url | `{url}` |
| cloze-body | `{cloze-body}` |
| cloze-prefix | `{cloze-prefix}` |
| close-suffix | `{cloze-suffix}` |
| conjugation | `{conjugation}` |
| expression | `{expression}` |
| frequencies | `{frequencies}` |

*Leave other fields (Notes, Image, Pitch Accent) empty or customize as needed.*

---

## Usage / Использование

Click the "+" button in Yomitan popup to create cards. Cards will have:
- Keyword highlighted in **red**
- Translation in gray
- Context sentence auto-added
- Audio attached

---

## Customization / Настройка стилей

Edit the note type `Yomitan Close GERMAN` in Anki:
- Go to **Manage Note Types**
- Select the model and edit CSS

---

## Requirements

- Anki 21+
- Yomitan / Yomichan browser extension
- AnkiConnect add-on
