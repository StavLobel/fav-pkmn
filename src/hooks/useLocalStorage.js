import { useState, useCallback } from 'react';
import * as storage from '../utils/storage';

export function useLocalStorage() {
  const [state, setState] = useState(() => storage.getState());

  const refresh = useCallback(() => {
    setState(storage.getState());
  }, []);

  const updateGen = useCallback((genId, data) => {
    const newState = storage.updateGeneration(genId, data);
    setState(newState);
    return newState;
  }, []);

  const updateGlobal = useCallback((data) => {
    const newState = storage.updateGlobal(data);
    setState(newState);
    return newState;
  }, []);

  const reset = useCallback(() => {
    storage.resetAll();
    setState(storage.getDefaultState());
  }, []);

  return { state, refresh, updateGen, updateGlobal, reset };
}
