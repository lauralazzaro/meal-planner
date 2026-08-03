// The API speaks canonical English keys; the UI speaks Italian. This file is
// the single place where the two meet, so a label change never has to be
// hunted down across pages and components.

export const DAY_LABELS = {
  MONDAY: 'lunedì',
  TUESDAY: 'martedì',
  WEDNESDAY: 'mercoledì',
  THURSDAY: 'giovedì',
  FRIDAY: 'venerdì',
  SATURDAY: 'sabato',
  SUNDAY: 'domenica',
};

// Week order as shown to the user: Monday first.
export const DAYS = Object.keys(DAY_LABELS);

// Date.getDay() indexes from Sunday, so this array is deliberately ordered
// differently from DAYS. Do not replace one with the other.
export const DAY_KEYS_BY_JS_INDEX = [
  'SUNDAY',
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
];

export const MEAL_LABELS = {
  BREAKFAST: 'Colazione',
  LUNCH: 'Pranzo',
  DINNER: 'Cena',
};

export const MEALS = Object.keys(MEAL_LABELS);

export const CATEGORY_LABELS = {
  VEGETABLES: 'Verdura',
  FRUIT: 'Frutta',
  MEAT_AND_FISH: 'Carne e pesce',
  PASTA_AND_GRAINS: 'Pasta e cereali',
  DAIRY: 'Latticini',
  PANTRY: 'Dispensa',
  BEVERAGES: 'Bevande',
  HOUSEHOLD: 'Casa',
  OTHER: 'Altro',
};

export const CATEGORIES = Object.keys(CATEGORY_LABELS);
