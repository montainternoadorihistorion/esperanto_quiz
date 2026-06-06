export const BASE_POINTS = 10;
export const STREAK_BONUS = 0.5;
export const SENTENCE_SCORE_SCALE = 2.0 / 1.5;
export const SENTENCE_STREAK_SCALE = 2.0;
export const VOCAB_ACCURACY_BONUS = 5.0;
export const SENTENCE_ACCURACY_BONUS = 10.0;
export const SPARTAN_SCORE_MULTIPLIER = 0.7;


export function computeResultSummary(session) {
  const total = session.questions.length;
  const correct = session.correct;
  const accuracy = total ? correct / total : 0;
  const accuracyBonus = accuracy * total * (
    session.settings.mode === "sentence" ? SENTENCE_ACCURACY_BONUS : VOCAB_ACCURACY_BONUS
  );
  const points = session.mainPoints + session.spartanScaledPoints + accuracyBonus;
  return {
    total,
    correct,
    accuracy,
    accuracyBonus,
    points,
  };
}


export function scoreForCorrect(question, streak) {
  const streakCount = Math.max(0, streak - 1);
  if (question.mode === "sentence") {
    const base = (Number(question.level) + 11.5) * SENTENCE_SCORE_SCALE;
    return base + streakCount * STREAK_BONUS * SENTENCE_STREAK_SCALE;
  }
  return BASE_POINTS * getStageFactor(question.stages) + streakCount * STREAK_BONUS;
}


export function scaleSpartanPoints(points) {
  return Number(points) * SPARTAN_SCORE_MULTIPLIER;
}


export function getStageFactor(stages) {
  if (stages.some((stage) => stage.includes("advanced"))) {
    return 1.6;
  }
  if (stages.some((stage) => stage.includes("intermediate"))) {
    return 1.3;
  }
  return 1.0;
}


export function buildVocabGroups(entries, seed) {
  const rng = mulberry32(clampInteger(seed, 1, 8192, 1));
  const byPos = new Map();
  entries.forEach((entry) => {
    const pos = entry.pos === "personal_pronoun" ? "pronoun" : entry.pos;
    const normalized = { ...entry, pos };
    if (!byPos.has(pos)) {
      byPos.set(pos, []);
    }
    byPos.get(pos).push(normalized);
  });

  const groups = [];
  [...byPos.entries()].forEach(([pos, items]) => {
    const buckets = splitByLevel(items);
    const sublevels = mergeSmallSublevels(buildSublevels(buckets));
    sublevels.forEach(({ labels, words }) => {
      groups.push(...splitIntoGroups(labels, words, pos, rng));
    });
  });
  return groups;
}


export function splitByLevel(entries) {
  const sorted = [...entries].sort((a, b) => Number(a.level) - Number(b.level));
  const [beginner, intermediate] = allocateByRatio(sorted.length, [55, 65, 120]);
  return {
    beginner: sorted.slice(0, beginner),
    intermediate: sorted.slice(beginner, beginner + intermediate),
    advanced: sorted.slice(beginner + intermediate),
  };
}


export function buildSublevels(buckets) {
  const ordered = [];
  [
    ["beginner", 3],
    ["intermediate", 3],
    ["advanced", 6],
  ].forEach(([stage, parts]) => {
    evenChunks(buckets[stage] || [], parts).forEach((chunk, index) => {
      if (chunk.length) {
        ordered.push({ labels: [`${stage}_${index + 1}`], words: [...chunk] });
      }
    });
  });
  return ordered;
}


export function mergeSmallSublevels(sublevels) {
  if (!sublevels.length) {
    return [];
  }
  const merged = [];
  let current = {
    labels: [...sublevels[0].labels],
    words: [...sublevels[0].words],
  };
  sublevels.slice(1).forEach((sublevel) => {
    if (current.words.length < 20) {
      current.labels.push(...sublevel.labels);
      current.words.push(...sublevel.words);
    } else {
      merged.push(current);
      current = {
        labels: [...sublevel.labels],
        words: [...sublevel.words],
      };
    }
  });
  if (current.words.length < 20 && merged.length) {
    const previous = merged.pop();
    previous.labels.push(...current.labels);
    previous.words.push(...current.words);
    merged.push(previous);
  } else {
    merged.push(current);
  }
  return merged;
}


export function splitIntoGroups(labels, words, pos, rng) {
  const shuffled = shuffle([...words], rng);
  const total = shuffled.length;
  const sizes = groupSizes(total);
  let cursor = 0;
  return sizes.map((size, index) => {
    const entries = shuffled.slice(cursor, cursor + size);
    cursor += size;
    return {
      id: `${pos}:${labels.join("+")}:g${index + 1}`,
      pos,
      stages: [...labels],
      indexLabel: `G${index + 1}`,
      entries,
    };
  });
}


export function groupSizes(total) {
  if (total <= 30) {
    return [total];
  }
  if (total <= 39) {
    const half = Math.floor(total / 2);
    return [half, total - half];
  }
  const count = chooseGroupCount(total);
  const base = Math.floor(total / count);
  const extra = total % count;
  return Array.from({ length: count }, (_, index) => base + (index < extra ? 1 : 0));
}


export function chooseGroupCount(total) {
  const lower = Math.ceil(total / 30);
  const upper = Math.max(lower, Math.floor(total / 20));
  let best = lower;
  let bestDistance = Number.POSITIVE_INFINITY;
  for (let count = lower; count <= upper; count += 1) {
    const distance = Math.abs(total / count - 25);
    if (distance < bestDistance) {
      best = count;
      bestDistance = distance;
    }
  }
  return best;
}


export function allocateByRatio(total, weights) {
  if (total <= 0) {
    return weights.map(() => 0);
  }
  const sum = weights.reduce((acc, value) => acc + value, 0);
  const raw = weights.map((weight) => total * weight / sum);
  const floors = raw.map(Math.floor);
  let remainder = total - floors.reduce((acc, value) => acc + value, 0);
  const order = raw
    .map((value, index) => ({ index, fraction: value - floors[index] }))
    .sort((a, b) => b.fraction - a.fraction);
  let cursor = 0;
  while (remainder > 0) {
    floors[order[cursor % order.length].index] += 1;
    remainder -= 1;
    cursor += 1;
  }
  return floors;
}


export function evenChunks(items, parts) {
  const base = Math.floor(items.length / parts);
  const extra = items.length % parts;
  let cursor = 0;
  return Array.from({ length: parts }, (_, index) => {
    const size = base + (index < extra ? 1 : 0);
    const chunk = items.slice(cursor, cursor + size);
    cursor += size;
    return chunk;
  });
}


function shuffle(items, rng) {
  for (let index = items.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(rng() * (index + 1));
    [items[index], items[swapIndex]] = [items[swapIndex], items[index]];
  }
  return items;
}


function mulberry32(seed) {
  let value = seed >>> 0;
  return function next() {
    value += 0x6D2B79F5;
    let mixed = value;
    mixed = Math.imul(mixed ^ mixed >>> 15, mixed | 1);
    mixed ^= mixed + Math.imul(mixed ^ mixed >>> 7, mixed | 61);
    return ((mixed ^ mixed >>> 14) >>> 0) / 4294967296;
  };
}


function clampInteger(value, min, max, fallback) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return Math.min(max, Math.max(min, parsed));
}
