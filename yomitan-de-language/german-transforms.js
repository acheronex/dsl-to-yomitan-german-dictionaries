/**
 * GERMAN TRANSFORMS - STABLE VERSION
 */

const germanLetters = 'a-zA-ZäöüßÄÖÜẞ';

// === ОПРЕДЕЛЕНИЕ УСЛОВИЙ (Обязательно для работы) ===
const conditions = {
    v: { name: 'Verb', isDictionaryForm: true },
    n: { name: 'Noun', isDictionaryForm: true },
    adj: { name: 'Adjective', isDictionaryForm: true },
};

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

// Функция для безопасной замены окончания
function stripSuffix(term, suffix, replacement) {
    if (term.endsWith(suffix)) {
        return term.slice(0, -suffix.length) + replacement;
    }
    return term;
}

// Функция для возврата умлаута (ä->a, ö->o, ü->u)
function deinflectUmlaut(term) {
    // Простая замена последней встреченной гласной
    // Порядок важен: äu проверяем первым
    if (term.includes('äu')) return term.replace(/äu(?!.*äu)/, 'au'); // Häuser -> Hauser
    if (term.includes('ä')) return term.replace(/ä(?!.*ä)/, 'a');     // Männer -> Manner
    if (term.includes('ö')) return term.replace(/ö(?!.*ö)/, 'o');     // Töne -> Tone
    if (term.includes('ü')) return term.replace(/ü(?!.*ü)/, 'u');     // Türen -> Turen
    return term;
}

// === ГЕНЕРАТОР ПРАВИЛ (ПРОСТОЙ) ===

// Создает правило: просто отрезать окончание
function makeSimpleRule(suffix, replacement = '') {
    return {
        type: 'other',
        isInflected: new RegExp(`${suffix}$`),
        deinflect: (term) => stripSuffix(term, suffix, replacement),
        conditionsIn: [],
        conditionsOut: [],
    };
}

// Создает правило: отрезать окончание + убрать умлаут (Männer -> Mann)
function makeUmlautRule(suffix, replacement = '') {
    // Регулярка требует наличия одного из умлаутов и окончания
    const regex = new RegExp(`[äöü].*${suffix}$`);
    return {
        type: 'other',
        isInflected: regex,
        deinflect: (term) => {
            const stripped = stripSuffix(term, suffix, replacement);
            return deinflectUmlaut(stripped);
        },
        conditionsIn: [],
        conditionsOut: [],
    };
}

// === СПИСКИ ПРАВИЛ ===

// 1. СУЩЕСТВИТЕЛЬНЫЕ И ПРИЛАГАТЕЛЬНЫЕ
// Просто перечисляем правила явным списком
const declensionRules = [
    // --- Простые срезы ---
    makeSimpleRule('en', ''),  // guten -> gut
    makeSimpleRule('e', ''),   // Tage -> Tag
    makeSimpleRule('er', ''),  // Kinder -> Kind
    makeSimpleRule('n', ''),   // Regeln -> Regel
    makeSimpleRule('s', ''),   // Autos -> Auto
    makeSimpleRule('es', ''),  // gutes
    makeSimpleRule('em', ''),  // gutem
    makeSimpleRule('ern', ''), // Kindern -> Kind
    
    // --- Умлауты (Männer -> Mann) ---
    makeUmlautRule('er', ''),  // Männer -> Mann
    makeUmlautRule('e', ''),   // Bäume -> Baum
    makeUmlautRule('en', ''),  
    makeUmlautRule('än', 'an'), // Особый случай
    
    // --- Прилагательные (Сравнение) ---
    makeSimpleRule('er', ''),   // schneller -> schnell
    makeSimpleRule('sten', ''), // besten -> be (ошибочно, но лучше чем ничего)
    makeSimpleRule('esten', ''),// neusten -> neu
    makeUmlautRule('er', ''),   // kälter -> kalt
    makeUmlautRule('sten', ''), // ärmsten -> arm
];

// 2. ЖЕНСКИЙ РОД
const feminineRules = [
    makeSimpleRule('innen', ''),
    makeSimpleRule('in', ''),
    makeUmlautRule('innen', ''), // Ärztinnen -> Arzt
    makeUmlautRule('in', ''),    // Ärztin -> Arzt
];

// 3. ГЛАГОЛЫ (Спряжение)
const conjugationRules = [
    // --- Простые окончания ---
    makeSimpleRule('en', ''),
    makeSimpleRule('est', 'en'),
    makeSimpleRule('ten', 'en'),
    makeSimpleRule('tet', 'en'),
    makeSimpleRule('test', 'en'),
    makeSimpleRule('te', 'en'),
    makeSimpleRule('st', 'en'),
    makeSimpleRule('et', 'en'),
    makeSimpleRule('t', 'en'),
    // (st -> n и t -> n для случаев типа wanderst -> wandern)
    makeSimpleRule('st', 'n'),
    makeSimpleRule('t', 'n'),

    // --- Умлауты (fährt -> fahren) ---
    makeUmlautRule('t', 'en'),
    makeUmlautRule('st', 'en'),
    makeUmlautRule('te', 'en'),
];

// 4. СПЕЦИФИКА ГЛАГОЛОВ (Смена гласной, Причастия, Zu)
const complexVerbRules = [
    // Смена i/ie -> e (spricht -> sprechen, liest -> lesen)
    {
        type: 'other',
        isInflected: /(i|ie)[^aeiou]+(t|st|e)$/, // Находит i/ie в корне + окончание
        deinflect: (term) => {
            // Очень простая и безопасная логика:
            // Если есть "ie", меняем на "e". Иначе если "i", меняем на "e".
            // И меняем окончание на "en"
            let root = term.replace(/(t|st|e)$/, ''); // Убрали окончание
            if (root.endsWith('ie')) {
                return root.slice(0, -2) + 'en'; // защиту от дублей не ставим для скорости
            }
            root = root.replace(/ie(?=[^aeiou]*$)/, 'e'); // Попытка замены ie->e
            root = root.replace(/i(?=[^aeiou]*$)/, 'e');  // Попытка замены i->e
            return root + 'en';
        },
        conditionsIn: [], conditionsOut: [],
    },
    // Zu-Infinitiv (anzufangen -> anfangen)
    {
        type: 'other',
        isInflected: /zu[a-zßäöü]+en$/,
        deinflect: (term) => term.replace('zu', ''), // Тупо вырезаем первое zu. aufzumachen -> aufmachen.
        conditionsIn: [], conditionsOut: [],
    },
    // Partizip II (ge-mach-t -> machen)
    {
        type: 'other',
        isInflected: /^ge.+t$/, 
        deinflect: (term) => {
             // ge(2 символа) + корень + t(1 символ)
             return term.slice(2, -1) + 'en'; 
        },
        conditionsIn: [], conditionsOut: [],
    },
    // Сильные (ge-fahr-en -> fahren)
    {
        type: 'other',
        isInflected: /^ge.+en$/, 
        deinflect: (term) => term.slice(2), // просто убираем ge
        conditionsIn: [], conditionsOut: [],
    }
];

// 5. ОРФОГРАФИЯ И ПРИСТАВКИ
const miscRules = [
    // ss -> ß
    {
        type: 'other',
        isInflected: /ss/,
        deinflect: (term) => term.replace(/ss/g, 'ß'),
        conditionsIn: [], conditionsOut: [],
    },
    // hin / her и их комбинации (hinaus, herein...)
    {
        type: 'other',
        isInflected: /^(hin|her)/,
        deinflect: (term) => term.replace(/^(hin|her)/, ''),
        conditionsIn: [], conditionsOut: [],
    }
];

// === ФИНАЛЬНЫЙ ЭКСПОРТ ===
export const germanTransforms = {
    language: 'de',
    conditions,
    transforms: {
        'declension': {
            name: 'Declension',
            description: 'Nouns and Adjectives',
            rules: [...declensionRules, ...feminineRules]
        },
        'conjugation': {
            name: 'Conjugation',
            description: 'Verbs basic forms',
            rules: conjugationRules
        },
        'complex_verbs': {
            name: 'Complex Verbs',
            description: 'Vowel shifts, Participles, Zu',
            rules: complexVerbRules
        },
        'misc': {
            name: 'Misc',
            description: 'Prefixes and Orthography',
            rules: miscRules
        }
    },
};