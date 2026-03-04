import { describe, it, expect } from 'vitest';
import { GENERATIONS as generations } from '../generations';

const EXPECTED_COUNTS = {
  1: 151,
  2: 100,
  3: 135,
  4: 107,
  5: 156,
  6: 72,
  7: 88,
  8: 96,
  9: 120,
};

describe('Generations Data', () => {
  it('UT-GEN-01: contains 9 generations', () => {
    expect(generations).toHaveLength(9);
  });

  it('UT-GEN-02: Gen 1 range is 1-151', () => {
    const gen1 = generations.find((g) => g.id === 1);
    expect(gen1.startId).toBe(1);
    expect(gen1.endId).toBe(151);
  });

  it('UT-GEN-03: no ID gaps between gens', () => {
    for (let i = 0; i < generations.length - 1; i++) {
      expect(generations[i].endId + 1).toBe(generations[i + 1].startId);
    }
  });

  it('UT-GEN-04: each gen has required fields', () => {
    generations.forEach((gen) => {
      expect(gen).toHaveProperty('id');
      expect(gen).toHaveProperty('name');
      expect(gen).toHaveProperty('startId');
      expect(gen).toHaveProperty('endId');
      expect(gen).toHaveProperty('starterIds');
      expect(gen.starterIds).toHaveLength(3);
    });
  });

  it('UT-GEN-05: Pokemon count per gen', () => {
    generations.forEach((gen) => {
      const count = gen.endId - gen.startId + 1;
      expect(count).toBe(EXPECTED_COUNTS[gen.id]);
    });
  });
});
