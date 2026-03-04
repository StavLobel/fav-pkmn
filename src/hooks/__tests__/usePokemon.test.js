import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { usePokemon, usePokemonBatch } from '../usePokemon';

const PIKACHU_RESPONSE = {
  id: 25,
  name: 'pikachu',
  sprites: {
    front_default:
      'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png',
  },
};

const CHARIZARD_RESPONSE = {
  id: 6,
  name: 'charizard',
  sprites: {
    front_default:
      'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png',
  },
};

function createFetchMock(responseMap) {
  return vi.fn((url) => {
    const id = url.match(/\/(\d+)\/?$/)?.[1];
    const data = responseMap[id];
    if (!data) {
      return Promise.reject(new Error('Not found'));
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data),
    });
  });
}

describe('usePokemon', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('HT-PK-01: fetches Pokemon by ID', async () => {
    globalThis.fetch = createFetchMock({ '25': PIKACHU_RESPONSE });

    const { result } = renderHook(() => usePokemon(25));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeTruthy();
    expect(result.current.data.name).toBe('pikachu');
    expect(result.current.data.sprite).toBeTruthy();
    expect(result.current.error).toBeNull();
  });

  it('HT-PK-02: caches fetched data', async () => {
    const mockFetch = createFetchMock({ '25': PIKACHU_RESPONSE });
    globalThis.fetch = mockFetch;

    const { result, rerender } = renderHook(
      ({ id }) => usePokemon(id),
      { initialProps: { id: 25 } }
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const callCountAfterFirst = mockFetch.mock.calls.length;

    rerender({ id: 25 });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(mockFetch.mock.calls.length).toBe(callCountAfterFirst);
  });

  it('HT-PK-03: handles fetch error', async () => {
    globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

    const { result } = renderHook(() => usePokemon(999));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.data).toBeNull();
  });

  it('HT-PK-04: fetches batch of Pokemon', async () => {
    globalThis.fetch = createFetchMock({
      '25': PIKACHU_RESPONSE,
      '6': CHARIZARD_RESPONSE,
    });

    const { result } = renderHook(() => usePokemonBatch([25, 6]));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(Object.keys(result.current.dataMap)).toHaveLength(2);
    expect(result.current.dataMap[25].name).toBe('pikachu');
    expect(result.current.dataMap[6].name).toBe('charizard');
  });
});
