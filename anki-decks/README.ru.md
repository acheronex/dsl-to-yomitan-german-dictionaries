# Anki колода для Yomitan (Немецкий)

Предварительно настроенная колода Anki для изучения немецкого языка с Yomitan.

## Возможности

- **Правильные поля** — expression, reading, meaning, sentence, audio, conjugation, frequencies
- **Собственная стилизация** — ключевое слово выделено красным, перевод серым
- **Готова к использованию** — импортируйте и подключите к Yomitan
- **Примеры карточек** — тестовые записи включены

---

## Быстрая настройка / Quick Setup

### 1. Импорт колоды / Import Deck

Дважды щелкните по `German Yomitan.apkg` для импорта в Anki.

### 2. Установка дополнений / Install Anki Add-ons

Установите эти дополнения в Anki:
- **AnkiConnect** — мост между браузером и Anki
- **AwesomeTTS** — озвучка текста
- **Google Translate** — быстрый перевод

### 3. Настройка Yomitan / Configure Yomitan

1. В настройках Yomitan включите интеграцию с Anki
2. Перейдите в **Configure Anki card format**
3. Выберите:
   - **Deck**: `Default`
   - **Model**: `Yomitan Close GERMAN`

### 4. Сопоставление полей / Field Mapping

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

*Другие поля (Notes, Image, Pitch Accent) оставьте пустыми или настройте по желанию.*

---

## Использование / Usage

Нажмите кнопку "+" в всплывающем окне Yomitan для создания карточек. Карточки будут иметь:
- Ключевое слово выделено **красным**
- Перевод серым цветом
- Контекст (предложение) добавляется автоматически
- Аудио прикрепляется

---

## Настройка стилей / Customization

Редактируйте тип заметки `Yomitan Close GERMAN` в Anki:
- Откройте **Управление типами заметок**
- Выберите модель и отредактируйте CSS

---

## Требования / Requirements

- Anki 21+
- Расширение Yomitan / Yomichan для браузера
- Дополнение AnkiConnect
