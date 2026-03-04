import { describe, it, expect } from 'vitest';
import { calculateExpectedScore, updateRatings } from '../elo';

describe('Elo Algorithm', () => {
  describe('calculateExpectedScore', () => {
    it('UT-ELO-01: calculates expected score', () => {
      const expected = calculateExpectedScore(1500, 1200);
      const formula = 1 / (1 + Math.pow(10, (1200 - 1500) / 400));
      expect(expected).toBeCloseTo(formula, 5);
    });

    it('UT-ELO-06: equal ratings produce equal expected scores', () => {
      const expected = calculateExpectedScore(1500, 1500);
      expect(expected).toBeCloseTo(0.5, 5);
    });
  });

  describe('updateRatings', () => {
    it('UT-ELO-02: winner gains rating', () => {
      const { newWinnerRating } = updateRatings(1500, 1500);
      expect(newWinnerRating).toBeGreaterThan(1500);
    });

    it('UT-ELO-03: loser loses rating', () => {
      const { newLoserRating } = updateRatings(1500, 1500);
      expect(newLoserRating).toBeLessThan(1500);
    });

    it('UT-ELO-04: zero-sum updates', () => {
      const { newWinnerRating, newLoserRating } = updateRatings(1500, 1400);
      const winnerGain = newWinnerRating - 1500;
      const loserLoss = 1400 - newLoserRating;
      expect(winnerGain).toBeCloseTo(loserLoss, 5);
    });

    it('UT-ELO-05: upset produces larger swing', () => {
      const upset = updateRatings(1200, 1600);
      const expected = updateRatings(1600, 1200);

      const upsetGain = upset.newWinnerRating - 1200;
      const expectedGain = expected.newWinnerRating - 1600;

      expect(upsetGain).toBeGreaterThan(expectedGain);
    });

    it('UT-ELO-07: K-factor controls magnitude', () => {
      const lowK = updateRatings(1500, 1500, 16);
      const highK = updateRatings(1500, 1500, 64);

      const lowKChange = lowK.newWinnerRating - 1500;
      const highKChange = highK.newWinnerRating - 1500;

      expect(highKChange).toBeGreaterThan(lowKChange);
      expect(highKChange / lowKChange).toBeCloseTo(4, 1);
    });
  });
});
