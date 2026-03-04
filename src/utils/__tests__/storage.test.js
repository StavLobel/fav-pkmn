import { describe, it, expect, beforeEach } from 'vitest';
import {
  STORAGE_KEY,
  getState,
  saveState,
  getGeneration,
  updateGeneration,
  resetAll,
} from '../storage';

const DEFAULT_STATE = { gens: {}, global: { status: 'not_started', top10: null } };

describe('Storage Utilities', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('UT-STR-01: initializes empty state', () => {
    const state = getState();
    expect(state).toEqual(DEFAULT_STATE);
  });

  it('UT-STR-02: saves and loads state', () => {
    const testState = {
      gens: { '1': { status: 'in_progress' } },
      global: { status: 'not_started', top10: null },
    };
    saveState(testState);
    const loaded = getState();
    expect(loaded).toEqual(testState);
  });

  it('UT-STR-03: updates generation status', () => {
    updateGeneration('1', { status: 'in_progress' });
    updateGeneration('2', { status: 'completed' });

    const gen1 = getGeneration('1');
    const gen2 = getGeneration('2');

    expect(gen1.status).toBe('in_progress');
    expect(gen2.status).toBe('completed');
  });

  it('UT-STR-04: resets all progress', () => {
    updateGeneration('1', { status: 'completed' });
    resetAll();
    const state = getState();
    expect(state).toEqual(DEFAULT_STATE);
  });

  it('UT-STR-05: handles corrupted data', () => {
    localStorage.setItem(STORAGE_KEY, '{invalid json!!!');
    const state = getState();
    expect(state).toEqual(DEFAULT_STATE);
  });

  it('UT-STR-06: stores Top 10 for generation', () => {
    const top10 = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      name: `pokemon-${i + 1}`,
      rating: 1500 - i * 10,
    }));
    updateGeneration('1', { status: 'completed', top10 });

    const gen1 = getGeneration('1');
    expect(gen1.top10).toHaveLength(10);
    expect(gen1.top10[0].id).toBe(1);
  });
});
