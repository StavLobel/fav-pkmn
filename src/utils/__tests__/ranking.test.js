import { describe, it, expect } from 'vitest';
import {
  shuffleArray,
  createGroups,
  recordSelection,
  buildCandidatePool,
  getNextPair,
  checkStability,
  getTopN,
  isMaxComparisonsReached,
} from '../ranking';

describe('Ranking Utilities', () => {
  describe('createGroups', () => {
    it('UT-RNK-01: groups Pokemon into sets of 4', () => {
      const ids = Array.from({ length: 12 }, (_, i) => i + 1);
      const groups = createGroups(ids, 4);
      expect(groups).toHaveLength(3);
      groups.forEach((group) => expect(group).toHaveLength(4));
    });

    it('UT-RNK-02: handles remainder group', () => {
      const ids = Array.from({ length: 14 }, (_, i) => i + 1);
      const groups = createGroups(ids, 4);
      expect(groups).toHaveLength(4);
      expect(groups[3]).toHaveLength(2);
    });
  });

  describe('shuffleArray', () => {
    it('UT-RNK-03: shuffles Pokemon', () => {
      const original = Array.from({ length: 50 }, (_, i) => i + 1);
      const shuffled1 = shuffleArray(original);
      const shuffled2 = shuffleArray(original);

      expect(shuffled1).toHaveLength(original.length);
      expect(shuffled1).toEqual(expect.arrayContaining(original));
      expect(
        shuffled1.some((val, idx) => val !== original[idx]) ||
          shuffled2.some((val, idx) => val !== original[idx])
      ).toBe(true);
    });
  });

  describe('recordSelection', () => {
    it('UT-RNK-04: increments score on selection', () => {
      const scores = { 1: 0, 2: 0, 3: 0 };
      const updated = recordSelection(scores, 2);
      expect(updated[2]).toBe(1);
      expect(updated[1]).toBe(0);
      expect(updated[3]).toBe(0);
    });
  });

  describe('buildCandidatePool', () => {
    it('UT-RNK-05: builds candidate pool from top scores', () => {
      const scores = {};
      for (let i = 1; i <= 151; i++) {
        scores[i] = i;
      }
      const pool = buildCandidatePool(scores, 151);
      pool.forEach((id) => {
        expect(scores[id]).toBeGreaterThanOrEqual(scores[pool[pool.length - 1]]);
      });
    });

    it('UT-RNK-06: candidate pool size scales with gen', () => {
      const scores = {};
      for (let i = 1; i <= 72; i++) {
        scores[i] = i;
      }
      const pool = buildCandidatePool(scores, 72);
      expect(pool.length).toBeGreaterThanOrEqual(20);
    });

    it('UT-RNK-07: candidate pool capped at 30', () => {
      const scores = {};
      for (let i = 1; i <= 200; i++) {
        scores[i] = i;
      }
      const pool = buildCandidatePool(scores, 200);
      expect(pool.length).toBeLessThanOrEqual(30);
    });
  });

  describe('getNextPair', () => {
    it('UT-RNK-08: matchmaking pairs similar ratings', () => {
      const candidates = [1, 2, 3, 4, 5];
      const ratings = { 1: 1500, 2: 1510, 3: 1600, 4: 1400, 5: 1505 };
      const comparisons = {};
      const [a, b] = getNextPair(candidates, ratings, comparisons);

      expect(candidates).toContain(a);
      expect(candidates).toContain(b);
      expect(a).not.toBe(b);
    });
  });

  describe('checkStability', () => {
    it('UT-RNK-09: stability detection triggers', () => {
      const stableHistory = Array.from({ length: 15 }, () => 0.5);
      expect(checkStability(stableHistory, 2, 10)).toBe(true);
    });

    it('returns false for unstable history', () => {
      const unstableHistory = Array.from({ length: 15 }, (_, i) => i * 10);
      expect(checkStability(unstableHistory, 2, 10)).toBe(false);
    });
  });

  describe('isMaxComparisonsReached', () => {
    it('UT-RNK-10: max comparisons enforced', () => {
      expect(isMaxComparisonsReached(100, 20, 5)).toBe(true);
      expect(isMaxComparisonsReached(99, 20, 5)).toBe(false);
    });
  });

  describe('getTopN', () => {
    it('UT-RNK-11: extracts Top 10 from ratings', () => {
      const ratings = {};
      for (let i = 1; i <= 30; i++) {
        ratings[i] = 1400 + i * 10;
      }
      const top10 = getTopN(ratings, 10);
      expect(top10).toHaveLength(10);
      for (let i = 0; i < top10.length - 1; i++) {
        expect(top10[i].rating).toBeGreaterThanOrEqual(top10[i + 1].rating);
      }
    });
  });
});
