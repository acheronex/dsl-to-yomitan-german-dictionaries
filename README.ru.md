# Конвертер DSL to Yomitan для немецких словарей

Инструмент для конвертации немецких словарей DSL (ABBYY Lingvo) в формат Yomitan. Оптимизирован для работы с немецкими словарями (Duden, Langenscheidt, Universal), но поддерживает любые словари в формате DSL.

## Возможности

- Парсинг DSL файлов (UTF-16 кодировка)
- Конвертация тегов DSL в JSON структурированный контент Yomitan
- Автоматическое определение языка (De-De, De-Ru, Ru-De)
- Поддержка тёмной темы через CSS `prefers-color-scheme`
- Разбиение больших словарей на части по 10,000 статей

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/acheronex/dsl-to-yomitan-german-dictionaries.git
cd dsl-to-yomitan-german-dictionaries

# Создать виртуальное окружение
python3 -m venv venv

# Активировать виртуальное окружение
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

## Использование

```bash
python main.py --input "путь/к/папке/словаря" --output "out/"
```

### Пример: конвертация словаря Langenscheidt

```bash
python main.py \
  --input "LINGVO X3 DEUTSCH AS FORIEGN BY LANGENS DE_DE_DSL" \
  --output out/
```

## Где взять словари DSL

Инструмент работает с существующими словарями в формате DSL. Найти их можно:

- **Форумы GoldenDict** — сообщество и ресурсы
- **Ru-Board** — русские форумы о софте
- **Торренты** — различные коллекции словарей
- **Ваша установка GoldenDict/Lingvo**

*Внимание: словари DSL обычно являются проприетарными и требуют соответствующего лицензирования. Пожалуйста, соблюдайте авторские права.*

## Поддерживаемые словари

Протестировано и работает с:

- **Langenscheidt** — Deutsch als Fremdsprache (De-De)
- **Duden** — Das große Wörterbuch (De-De)
- **Duden** — Synonyme (De-De)
- **Duden** — Etymologie (De-De)
- **Universal** — De-Ru, Ru-De

## Лицензия

MIT License — подробности в файле LICENSE.

## Автор

Евгений Ерошев (GitHub: @acheronex)
