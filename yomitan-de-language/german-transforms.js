/**
 * GERMAN TRANSFORMS - STABLE VERSION (safer v2)
 */

const germanLetters = 'a-zA-ZäöüßÄÖÜẞ';

// === ОПРЕДЕЛЕНИЕ УСЛОВИЙ ===
const conditions = {
    v: { name: 'Verb', isDictionaryForm: true },
    n: { name: 'Noun', isDictionaryForm: true },
    adj: { name: 'Adjective', isDictionaryForm: true },
};

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
function stripSuffix(term, suffix, replacement) {
    if (term.endsWith(suffix)) {
        return term.slice(0, -suffix.length) + replacement;
    }
    return term;
}

function isValidLemma(term) {
    // Отсекаем мусор: пусто, слишком коротко, не-буквы
    return typeof term === 'string'
        && term.length >= 3
        && new RegExp(`^[${germanLetters}]+$`).test(term);
}

function safeResult(original, candidate) {
    if (!isValidLemma(candidate)) return original;
    if (candidate === original) return original;
    return candidate;
}

// Возврат умлаута (ä->a, ö->o, ü->u) только последнего вхождения
function deinflectUmlaut(term) {
    if (term.includes('äu')) return term.replace(/äu(?!.*äu)/, 'au');
    if (term.includes('ä')) return term.replace(/ä(?!.*ä)/, 'a');
    if (term.includes('ö')) return term.replace(/ö(?!.*ö)/, 'o');
    if (term.includes('ü')) return term.replace(/ü(?!.*ü)/, 'u');
    return term;
}

// === ГЕНЕРАТОР ПРАВИЛ ===
function makeSimpleRule(suffix, replacement = '', conditionsIn = [], conditionsOut = []) {
    return {
        type: 'other',
        isInflected: new RegExp(`${suffix}$`),
        deinflect: (term) => {
            const candidate = stripSuffix(term, suffix, replacement);
            return safeResult(term, candidate);
        },
        conditionsIn,
        conditionsOut,
    };
}

function makeUmlautRule(suffix, replacement = '', conditionsIn = [], conditionsOut = []) {
    const regex = new RegExp(`[äöü].*${suffix}$`);
    return {
        type: 'other',
        isInflected: regex,
        deinflect: (term) => {
            const stripped = stripSuffix(term, suffix, replacement);
            const candidate = deinflectUmlaut(stripped);
            return safeResult(term, candidate);
        },
        conditionsIn,
        conditionsOut,
    };
}

// === ПРАВИЛА ===

// 1) Существительные/прилагательные (сужено)
const declensionRules = [
    // сначала более специфичные длинные окончания
    makeSimpleRule('ern', '', ['n', 'adj'], ['n', 'adj']),
    makeSimpleRule('esten', '', ['adj'], ['adj']),
    makeSimpleRule('sten', '', ['adj'], ['adj']),
    makeSimpleRule('es', '', ['adj', 'n'], ['adj', 'n']),
    makeSimpleRule('em', '', ['adj'], ['adj']),
    makeSimpleRule('er', '', ['n', 'adj'], ['n', 'adj']),
    makeSimpleRule('en', '', ['n', 'adj'], ['n', 'adj']),
    makeSimpleRule('e', '', ['n', 'adj'], ['n', 'adj']),
    makeSimpleRule('n', '', ['n'], ['n']),
    makeSimpleRule('s', '', ['n'], ['n']),

    // umlaut-варианты
    makeUmlautRule('er', '', ['n', 'adj'], ['n', 'adj']),
    makeUmlautRule('en', '', ['n', 'adj'], ['n', 'adj']),
    makeUmlautRule('e', '', ['n', 'adj'], ['n', 'adj']),
];

// 2) Feminine forms
const feminineRules = [
    makeUmlautRule('innen', '', ['n'], ['n']), // Ärztinnen -> Arzt
    makeSimpleRule('innen', '', ['n'], ['n']),
    makeUmlautRule('in', '', ['n'], ['n']),    // Ärztin -> Arzt
    makeSimpleRule('in', '', ['n'], ['n']),
];

// 3) Глаголы
const conjugationRules = [
    // сначала длинные
    makeSimpleRule('test', 'en', ['v'], ['v']),
    makeSimpleRule('tet', 'en', ['v'], ['v']),
    makeSimpleRule('ten', 'en', ['v'], ['v']),
    makeSimpleRule('est', 'en', ['v'], ['v']),
    makeSimpleRule('te', 'en', ['v'], ['v']),
    makeSimpleRule('st', 'en', ['v'], ['v']),
    makeSimpleRule('et', 'en', ['v'], ['v']),
    makeSimpleRule('t', 'en', ['v'], ['v']),

    // альтернатива для wanderst -> wandern
    makeSimpleRule('st', 'n', ['v'], ['v']),
    makeSimpleRule('t', 'n', ['v'], ['v']),

    // базовое инфинитивное en (оставляем, но только для v)
    makeSimpleRule('en', '', ['v'], ['v']),

    // umlaut для глаголов
    makeUmlautRule('st', 'en', ['v'], ['v']),
    makeUmlautRule('te', 'en', ['v'], ['v']),
    makeUmlautRule('t', 'en', ['v'], ['v']),
];

// 4) Сложные глагольные
const complexVerbRules = [
    // liest/spricht -> lesen/sprechen (аккуратнее)
    {
        type: 'other',
        isInflected: /^[a-zäöüß]{4,}(t|st|e)$/, 
        deinflect: (term) => {
            let root = term.replace(/(st|t|e)$/, '');

            // Меняем только ближайшее к концу ie/i в корневой зоне
            const before = root;
            root = root.replace(/ie(?=[^aeiouäöü]*$)/, 'e');
            if (root === before) {
                root = root.replace(/i(?=[^aeiouäöü]*$)/, 'e');
            }

            const candidate = root + 'en';
            return safeResult(term, candidate);
        },
        conditionsIn: ['v'],
        conditionsOut: ['v'],
    },
    // zu-Infinitiv: удаляем только префиксное "zu"
    {
        type: 'other',
        isInflected: /^zu[a-zäöüß]+en$/, 
        deinflect: (term) => {
            const candidate = term.replace(/^zu/, '');
            return safeResult(term, candidate);
        },
        conditionsIn: ['v'],
        conditionsOut: ['v'],
    },
    // Partizip II weak: gemacht -> machen (более строго)
    {
        type: 'other',
        isInflected: /^ge[a-zäöüß]{3,}t$/, 
        deinflect: (term) => {
            const candidate = term.slice(2, -1) + 'en';
            return safeResult(term, candidate);
        },
        conditionsIn: ['v'],
        conditionsOut: ['v'],
    },
    // Partizip II strong: gefahren -> fahren
    {
        type: 'other',
        isInflected: /^ge[a-zäöüß]{3,}en$/, 
        deinflect: (term) => {
            const candidate = term.slice(2);
            return safeResult(term, candidate);
        },
        conditionsIn: ['v'],
        conditionsOut: ['v'],
    }
];

// 5) Прочее (ослаблено)
const miscRules = [
    // ss -> ß только если нет уже ß и есть хотя бы 1 гласная (грубый guard)
    {
        type: 'other',
        isInflected: /ss/,
        deinflect: (term) => {
            if (term.includes('ß')) return term;
            if (!/[aeiouäöü]/.test(term)) return term;
            const candidate = term.replace(/ss/g, 'ß');
            return safeResult(term, candidate);
        },
        conditionsIn: [],
        conditionsOut: [],
    },
    // Удаляем hin/her только в длинных словах (снижает ложные срабатывания)
    {
        type: 'other',
        isInflected: /^(hin|her)[a-zäöüß]{4,}$/, 
        deinflect: (term) => {
            const candidate = term.replace(/^(hin|her)/, '');
            return safeResult(term, candidate);
        },
        conditionsIn: ['v'],
        conditionsOut: ['v'],
    }
];

// === ЭКСПОРТ ===
export const germanTransforms = {
    language: 'de',
    conditions,
    transforms: {
        declension: {
            name: 'Declension',
            description: 'Nouns and Adjectives',
            rules: [...declensionRules, ...feminineRules]
        },
        conjugation: {
            name: 'Conjugation',
            description: 'Verbs basic forms',
            rules: conjugationRules
        },
        complex_verbs: {
            name: 'Complex Verbs',
            description: 'Vowel shifts, Participles, Zu',
            rules: complexVerbRules
        },
        misc: {
            name: 'Misc',
            description: 'Prefixes and Orthography',
            rules: miscRules
        }
    },
};
