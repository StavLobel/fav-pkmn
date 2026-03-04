export const GENERATIONS = [
  { id: 1, name: 'Kanto', startId: 1, endId: 151, starterIds: [1, 4, 7] },
  { id: 2, name: 'Johto', startId: 152, endId: 251, starterIds: [152, 155, 158] },
  { id: 3, name: 'Hoenn', startId: 252, endId: 386, starterIds: [252, 255, 258] },
  { id: 4, name: 'Sinnoh', startId: 387, endId: 493, starterIds: [387, 390, 393] },
  { id: 5, name: 'Unova', startId: 494, endId: 649, starterIds: [495, 498, 501] },
  { id: 6, name: 'Kalos', startId: 650, endId: 721, starterIds: [650, 653, 656] },
  { id: 7, name: 'Alola', startId: 722, endId: 809, starterIds: [722, 725, 728] },
  { id: 8, name: 'Galar', startId: 810, endId: 905, starterIds: [810, 813, 816] },
  { id: 9, name: 'Paldea', startId: 906, endId: 1025, starterIds: [906, 909, 912] },
];

export function getGeneration(genId) {
  return GENERATIONS.find((g) => g.id === Number(genId));
}

export function getGenPokemonIds(genId) {
  const gen = getGeneration(genId);
  if (!gen) return [];
  const ids = [];
  for (let i = gen.startId; i <= gen.endId; i++) {
    ids.push(i);
  }
  return ids;
}

export function getGenSize(genId) {
  const gen = getGeneration(genId);
  if (!gen) return 0;
  return gen.endId - gen.startId + 1;
}
