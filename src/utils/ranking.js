export function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export function createGroups(pokemonIds, groupSize = 4) {
  const groups = [];
  for (let i = 0; i < pokemonIds.length; i += groupSize) {
    groups.push(pokemonIds.slice(i, i + groupSize));
  }
  return groups;
}

export function recordSelection(scores, selectedId) {
  return {
    ...scores,
    [selectedId]: (scores[selectedId] || 0) + 1,
  };
}

export function buildCandidatePool(scores, genSize) {
  const poolSize = Math.max(20, Math.min(30, Math.ceil(genSize * 0.2)));

  const sorted = Object.entries(scores)
    .map(([id, score]) => ({ id: Number(id), score }))
    .sort((a, b) => b.score - a.score);

  return sorted.slice(0, poolSize).map((entry) => entry.id);
}

function pairKey(a, b) {
  return `${Math.min(a, b)}-${Math.max(a, b)}`;
}

export function getNextPair(candidates, ratings, comparisons) {
  let bestPair = null;
  let bestScore = Infinity;

  for (let i = 0; i < candidates.length; i++) {
    for (let j = i + 1; j < candidates.length; j++) {
      const a = candidates[i];
      const b = candidates[j];
      const ratingDiff = Math.abs((ratings[a] || 1500) - (ratings[b] || 1500));
      const compCount = comparisons[pairKey(a, b)] || 0;
      // Heavily penalize re-comparing the same pair
      const score = ratingDiff + compCount * 200;

      if (score < bestScore) {
        bestScore = score;
        bestPair = [a, b];
      }
    }
  }

  return bestPair;
}

export function checkStability(ratingHistory, threshold = 2, windowSize = 10) {
  if (ratingHistory.length < windowSize) return false;

  const recent = ratingHistory.slice(-windowSize);
  const avg = recent.reduce((sum, val) => sum + val, 0) / recent.length;

  return avg < threshold;
}

export function getTopN(ratings, n = 10) {
  return Object.entries(ratings)
    .map(([id, rating]) => ({ id: Number(id), rating }))
    .sort((a, b) => b.rating - a.rating)
    .slice(0, n);
}

export function isMaxComparisonsReached(totalComparisons, poolSize, factor = 5) {
  return totalComparisons >= poolSize * factor;
}
