import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../useLocalStorage';

const DEFAULT_STATE = { gens: {}, global: { status: 'not_started', top10: null } };

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('HT-LS-01: returns initial state', () => {
    const { result } = renderHook(() => useLocalStorage());
    expect(result.current.state).toEqual(DEFAULT_STATE);
  });

  it('HT-LS-02: persists state update', () => {
    const { result } = renderHook(() => useLocalStorage());

    act(() => {
      result.current.updateGen('1', { status: 'in_progress' });
    });

    expect(result.current.state.gens['1'].status).toBe('in_progress');

    const stored = JSON.parse(localStorage.getItem('favpoke_v1'));
    expect(stored.gens['1'].status).toBe('in_progress');
  });

  it('HT-LS-03: restores on remount', () => {
    const { result, unmount } = renderHook(() => useLocalStorage());

    act(() => {
      result.current.updateGen('3', { status: 'completed' });
    });

    unmount();

    const { result: result2 } = renderHook(() => useLocalStorage());
    expect(result2.current.state.gens['3'].status).toBe('completed');
  });

  it('HT-LS-04: reset clears storage', () => {
    const { result } = renderHook(() => useLocalStorage());

    act(() => {
      result.current.updateGen('1', { status: 'completed' });
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.state).toEqual(DEFAULT_STATE);
  });
});
