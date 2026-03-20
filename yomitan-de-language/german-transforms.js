/**
 * GERMAN TRANSFORMS - YOMITAN OPTIMIZED ULTIMATE VERSION
 * Включает: словари, защиту корней, приставки, умлауты И РАСЩЕПИТЕЛЬ КОМПАУНДОВ.
 */

const germanLetters = "a-zA-ZäöüßÄÖÜẞ";
const sepPrefixes =
  "ab|an|auf|aus|bei|dar|ein|empor|entgegen|entlang|fehl|fest|fort|gegenüber|gleich|her|heran|heraus|herein|hin|hinab|hinauf|hinaus|hinein|los|mit|nach|nieder|vor|voran|voraus|vorbei|weg|weiter|wieder|zu|zurück|zusammen";

// Самые частые корни составных существительных (Komposita)
const compoundRoots =
  "schule|straße|laden|haus|platz|weg|zimmer|auto|uhr|stadt|land|mann|frau|kind|buch|baum|tür|fenster|amt|anlage|arbeit|bild|blatt|dorf|fahrt|fall|frage|geld|gesellschaft|gesetz|gruppe|karte|kraft|maschine|mittel|plan|programm|raum|recht|spiel|stelle|system|teil|vertrag|wasser|werk|wirtschaft|zeit|ziel|zentrum";

// === ОПРЕДЕЛЕНИЕ УСЛОВИЙ ===
const conditions = {
  v: { name: "Verb", isDictionaryForm: true },
  n: { name: "Noun", isDictionaryForm: true },
  adj: { name: "Adjective", isDictionaryForm: true },
};

// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
function stripSuffix(term, suffix, replacement) {
  if (term.endsWith(suffix)) {
    return term.slice(0, -suffix.length) + replacement;
  }
  return term;
}

function deinflectUmlaut(term) {
  if (term.includes("äu")) return term.replace(/äu([^äöü]*)$/, "au$1");
  if (term.includes("ä")) return term.replace(/ä([^äöü]*)$/, "a$1");
  if (term.includes("ö")) return term.replace(/ö([^äöü]*)$/, "o$1");
  if (term.includes("ü")) return term.replace(/ü([^äöü]*)$/, "u$1");
  return term;
}

function makeSafeRule(suffix, replacement = "", minRootLength = 3) {
  return {
    type: "other",
    isInflected: new RegExp(`^.{${minRootLength},}${suffix}$`),
    deinflect: (term) => stripSuffix(term, suffix, replacement),
    conditionsIn: [],
    conditionsOut: [],
  };
}

function makeSafeUmlautRule(suffix, replacement = "", minRootLength = 3) {
  return {
    type: "other",
    isInflected: new RegExp(`^.*[äöü].*${suffix}$`),
    deinflect: (term) => {
      if (term.length - suffix.length < minRootLength) return term;
      const stripped = stripSuffix(term, suffix, replacement);
      return deinflectUmlaut(stripped);
    },
    conditionsIn: [],
    conditionsOut: [],
  };
}

// === СЛОВАРЬ ПРОБЛЕМНЫХ СУЩЕСТВИТЕЛЬНЫХ ===
const irregularNouns = {
  mütter: "mutter",
  müttern: "mutter",
  väter: "vater",
  vätern: "vater",
  brüder: "bruder",
  brüdern: "bruder",
  töchter: "tochter",
  töchtern: "tochter",
  äpfel: "apfel",
  äpfeln: "apfel",
  vögel: "vogel",
  vögeln: "vogel",
  gärten: "garten",
  häfen: "hafen",
  mäntel: "mantel",
  mänteln: "mantel",
  böden: "boden",
  fäden: "faden",
  gräben: "graben",
  öfen: "ofen",
  schäden: "schaden",
  nägel: "nagel",
  nägeln: "nagel",
  männer: "mann",
  männern: "mann",
  bücher: "buch",
  büchern: "buch",
  wälder: "wald",
  wäldern: "wald",
  blätter: "blatt",
  blättern: "blatt",
  dörfer: "dorf",
  dörfern: "dorf",
  dächer: "dach",
  dächern: "dach",
  gläser: "glas",
  gläsern: "glas",
  länder: "land",
  ländern: "land",
  ränder: "rand",
  rändern: "rand",
  geister: "geist",
  geistern: "geist",
  götter: "gott",
  göttern: "gott",
  wörter: "wort",
  wörtern: "wort",
  häuser: "haus",
  häusern: "haus",
  mäuler: "maul",
  mäulern: "maul",
  kinder: "kind",
  kindern: "kind",
  bilder: "bild",
  bildern: "bild",
  lieder: "lied",
  liedern: "lied",
  themen: "thema",
  zentren: "zentrum",
  museen: "museum",
  stadien: "stadion",
  praktika: "praktikum",
  lexika: "lexikon",
  firmen: "firma",
  villen: "villa",
  pizzen: "pizza",
  kameras: "kamera",
  rhythmen: "rhythmus",
  globen: "globus",
  klimata: "klima",
  risiken: "risiko",
  materialien: "material",
  prinzipien: "prinzip",
  studien: "studie",
  seen: "see",
  feen: "fee",
  ideen: "idee",
  armeen: "armee",
  eier: "ei",
  eiern: "ei",
  ski: "ski",
  skier: "ski",
  frauen: "frau",
  herren: "herr",
};

const irregularNounsRule = {
  type: "other",
  isInflected: new RegExp(`^(${Object.keys(irregularNouns).join("|")})$`, "i"),
  deinflect: (term) => {
    const lowerTerm = term.toLowerCase();
    const dictForm = irregularNouns[lowerTerm];
    if (dictForm) {
      return term[0] === term[0].toUpperCase()
        ? dictForm.charAt(0).toUpperCase() + dictForm.slice(1)
        : dictForm;
    }
    return term;
  },
  conditionsIn: [],
  conditionsOut: [],
};

// === ПРАВИЛО РАСЩЕПЛЕНИЯ КОМПАУНДОВ (Compound Splitter) ===
const compoundRule = {
  type: "other",
  // Ищем слова, которые ЗАКАНЧИВАЮТСЯ на один из частых корней,
  // но при этом имеют минимум 2 буквы перед ним (чтобы не отрезать само слово от себя)
  isInflected: new RegExp(`^.{2,}?(${compoundRoots})$`, "i"),
  deinflect: (term) => {
    const match = term.match(new RegExp(`(${compoundRoots})$`, "i"));
    if (match) {
      const root = match[1];
      // Возвращаем найденный корень с сохранением регистра исходного слова
      return term[0] === term[0].toUpperCase()
        ? root.charAt(0).toUpperCase() + root.slice(1)
        : root;
    }
    return term;
  },
  conditionsIn: [],
  conditionsOut: [],
};

// === СЛОВАРЬ НЕПРАВИЛЬНЫХ ГЛАГОЛОВ ===
const irregularVerbs = {
  bin: "sein",
  bist: "sein",
  ist: "sein",
  sind: "sein",
  seid: "sein",
  war: "sein",
  warst: "sein",
  waren: "sein",
  gewesen: "sein",
  hast: "haben",
  hat: "haben",
  hatte: "haben",
  hatten: "haben",
  gehabt: "haben",
  wirst: "werden",
  wird: "werden",
  wurde: "werden",
  wurden: "werden",
  geworden: "werden",
  kann: "können",
  kannst: "können",
  konnte: "können",
  gekonnt: "können",
  muss: "müssen",
  musst: "müssen",
  musste: "müssen",
  gemusst: "müssen",
  darf: "dürfen",
  darfst: "dürfen",
  durfte: "dürfen",
  gedurft: "dürfen",
  soll: "sollen",
  sollst: "sollen",
  sollte: "sollen",
  gesollt: "sollen",
  will: "wollen",
  willst: "wollen",
  wollte: "wollen",
  gewollt: "wollen",
  mag: "mögen",
  magst: "mögen",
  mochte: "mögen",
  gemocht: "mögen",
  möchte: "mögen",
  ging: "gehen",
  gingen: "gehen",
  gegangen: "gehen",
  kam: "kommen",
  kamen: "kommen",
  gekommen: "kommen",
  sah: "sehen",
  siehst: "sehen",
  sieht: "sehen",
  sahen: "sehen",
  gesehen: "sehen",
  zog: "ziehen",
  zogen: "ziehen",
  gezogen: "ziehen",
  tat: "tun",
  tust: "tun",
  tut: "tun",
  taten: "tun",
  getan: "tun",
  weiß: "wissen",
  weißt: "wissen",
  wusste: "wissen",
  gewusst: "wissen",
  brachte: "bringen",
  gebracht: "bringen",
  dachte: "denken",
  gedacht: "denken",
  nahm: "nehmen",
  nimmst: "nehmen",
  nimmt: "nehmen",
  nahmen: "nehmen",
  genommen: "nehmen",
  sprach: "sprechen",
  sprichst: "sprechen",
  spricht: "sprechen",
  sprachen: "sprechen",
  gesprochen: "sprechen",
  gab: "geben",
  gibst: "geben",
  gibt: "geben",
  gaben: "geben",
  gegeben: "geben",
  aß: "essen",
  isst: "essen",
  aßen: "essen",
  gegessen: "essen",
  las: "lesen",
  liest: "lesen",
  lasen: "lesen",
  gelesen: "lesen",
  schrieb: "schreiben",
  schrieben: "schreiben",
  geschrieben: "schreiben",
  blieb: "bleiben",
  blieben: "bleiben",
  geblieben: "bleiben",
  ließ: "lassen",
  lässt: "lassen",
  ließen: "lassen",
  gelassen: "lassen",
  fiel: "fallen",
  fällst: "fallen",
  fällt: "fallen",
  fielen: "fallen",
  gefallen: "fallen",
  hielt: "halten",
  hältst: "halten",
  hält: "halten",
  hielten: "halten",
  gehalten: "halten",
  stand: "stehen",
  standen: "stehen",
  gestanden: "stehen",
  fand: "finden",
  fanden: "finden",
  gefunden: "finden",
  verlor: "verlieren",
  verloren: "verlieren",
  bot: "bieten",
  boten: "bieten",
  geboten: "bieten",
  bat: "bitten",
  baten: "bitten",
  gebeten: "bitten",
  flog: "fliegen",
  flogen: "fliegen",
  geflogen: "fliegen",
  half: "helfen",
  hilfst: "helfen",
  hilft: "helfen",
  halfen: "helfen",
  geholfen: "helfen",
  lief: "laufen",
  läufst: "laufen",
  läuft: "laufen",
  liefen: "laufen",
  gelaufen: "laufen",
  lag: "liegen",
  lagen: "liegen",
  gelegen: "liegen",
  rief: "rufen",
  riefen: "rufen",
  gerufen: "rufen",
  schlug: "schlagen",
  schlägst: "schlagen",
  schlägt: "schlagen",
  schlugen: "schlagen",
  geschlagen: "schlagen",
  trug: "tragen",
  trägst: "tragen",
  trägt: "tragen",
  trugen: "tragen",
  getragen: "tragen",
  traf: "treffen",
  triffst: "treffen",
  trifft: "treffen",
  trafen: "treffen",
  getroffen: "treffen",
  trank: "trinken",
  tranken: "trinken",
  getrunken: "trinken",
  wusch: "waschen",
  wäschst: "waschen",
  wäscht: "waschen",
  wuschen: "waschen",
  gewaschen: "waschen",
};

const irregularVerbsRule = {
  type: "other",
  isInflected: new RegExp(`^(${Object.keys(irregularVerbs).join("|")})$`, "i"),
  deinflect: (term) => {
    const lowerTerm = term.toLowerCase();
    return irregularVerbs[lowerTerm] || term;
  },
  conditionsIn: [],
  conditionsOut: [],
};

// === ПРАВИЛА ОТДЕЛЯЕМЫХ ПРИСТАВОК ===
const separablePrefixRules = [
  {
    type: "other",
    isInflected: new RegExp(`^([a-zäöüß]+)\\s+(${sepPrefixes})$`, "i"),
    deinflect: (term) => {
      const match = term.match(
        new RegExp(`^([a-zäöüß]+)\\s+(${sepPrefixes})$`, "i")
      );
      if (!match) return term;
      let [, verb, prefix] = match;
      verb = verb.toLowerCase();
      prefix = prefix.toLowerCase();
      if (irregularVerbs[verb]) return prefix + irregularVerbs[verb];
      let root = verb.replace(/(est|test|ten|tet|te|e|st|et|t|en)$/, ""); // добавлено 'e'
      return prefix + root + "en";
    },
    conditionsIn: [],
    conditionsOut: [],
  },
  {
    type: "other",
    isInflected: new RegExp(`^(${sepPrefixes})ge(.{3,})t$`, "i"),
    deinflect: (term) =>
      term.replace(new RegExp(`^(${sepPrefixes})ge(.{3,})t$`, "i"), "$1$2en"),
    conditionsIn: [],
    conditionsOut: [],
  },
  {
    type: "other",
    isInflected: new RegExp(`^(${sepPrefixes})ge(.{3,}en)$`, "i"),
    deinflect: (term) =>
      term.replace(new RegExp(`^(${sepPrefixes})ge(.{3,}en)$`, "i"), "$1$2"),
    conditionsIn: [],
    conditionsOut: [],
  },
];

// === СПИСКИ ПРАВИЛ ===
const declensionRules = [
  makeSafeRule("en", "", 3),
  makeSafeRule("e", "", 3),
  makeSafeRule("er", "", 3),
  makeSafeRule("n", "", 2),
  makeSafeRule("s", "", 2),
  makeSafeRule("es", "", 3),
  makeSafeRule("em", "", 3),
  makeSafeRule("ern", "", 3),
  makeSafeUmlautRule("er", "", 3),
  makeSafeUmlautRule("e", "", 3),
  makeSafeUmlautRule("en", "", 3),
  makeSafeRule("sten", "", 2),
  makeSafeRule("esten", "", 2),
  makeSafeUmlautRule("sten", "", 2),
];

const feminineRules = [
  makeSafeRule("innen", "", 3),
  makeSafeRule("in", "", 3),
  makeSafeUmlautRule("innen", "", 3),
  makeSafeUmlautRule("in", "", 3),
];

const conjugationRules = [
  makeSafeRule("est", "en", 2),
  makeSafeRule("test", "en", 2),
  makeSafeRule("ten", "en", 2),
  makeSafeRule("tet", "en", 2),
  makeSafeRule("te", "en", 2),
  makeSafeRule("st", "en", 2),
  makeSafeRule("et", "en", 2),
  makeSafeRule("t", "en", 2),
  makeSafeRule("e", "en", 2), // ДОБАВЛЕНО ПРАВИЛО ДЛЯ gebe И komme
  makeSafeRule("st", "n", 3),
  makeSafeRule("t", "n", 3),
  makeSafeUmlautRule("t", "en", 2),
  makeSafeUmlautRule("st", "en", 2),
];

const complexVerbRules = [
  {
    type: "other",
    isInflected: /^(.*[^aeiou])(i|ie)([^aeiou]+)(t|st)$/,
    deinflect: (term) => {
      const match = term.match(/^(.*[^aeiou])(i|ie)([^aeiou]+)(t|st)$/);
      if (!match) return term;
      return match[1] + "e" + match[3] + "en";
    },
    conditionsIn: [],
    conditionsOut: [],
  },
  {
    type: "other",
    isInflected: /^(.{2,})zu(.{3,}en)$/,
    deinflect: (term) => term.replace(/^(.{2,})zu(.{3,}en)$/, "$1$2"),
    conditionsIn: [],
    conditionsOut: [],
  },
  {
    type: "other",
    isInflected: /^ge.{3,}t$/,
    deinflect: (term) => term.slice(2, -1) + "en",
    conditionsIn: [],
    conditionsOut: [],
  },
  {
    type: "other",
    isInflected: /^ge.{3,}en$/,
    deinflect: (term) => term.slice(2),
    conditionsIn: [],
    conditionsOut: [],
  },
];

const miscRules = [
  {
    type: "other",
    isInflected: /ss(t|en|te|e)?$/,
    deinflect: (term) =>
      term.replace(/ss(t|en|te|e)?$/, (match) => "ß" + match.slice(2)),
    conditionsIn: [],
    conditionsOut: [],
  },
];

// === ФИНАЛЬНЫЙ ЭКСПОРТ ===
export const germanTransforms = {
  language: "de",
  conditions,
  transforms: {
    declension: {
      name: "Declension",
      description: "Nouns and Adjectives",
      rules: [irregularNounsRule, ...declensionRules, ...feminineRules],
    },
    compound_nouns: {
      name: "Compound Splitter",
      description: "Splits unknown compound nouns to their root",
      // РАСЩЕПИТЕЛЬ ДОБАВЛЕН СЮДА
      rules: [compoundRule],
    },
    conjugation: {
      name: "Conjugation",
      description: "Verbs basic forms",
      rules: [irregularVerbsRule, ...conjugationRules],
    },
    separable_prefixes: {
      name: "Separable Prefixes",
      description: "Trennbare Verben",
      rules: separablePrefixRules,
    },
    complex_verbs: {
      name: "Complex Verbs",
      description: "Vowel shifts, Participles, Zu-infinitive",
      rules: complexVerbRules,
    },
    misc: {
      name: "Misc",
      description: "Orthography",
      rules: miscRules,
    },
  },
};
