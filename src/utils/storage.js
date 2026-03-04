const STORAGE_KEY = 'favpoke_v1';

const DEFAULT_STATE = {
  gens: {},
  global: { status: 'not_started', top10: null },
};

export function getState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return structuredClone(DEFAULT_STATE);
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object' || !parsed.gens) {
      return structuredClone(DEFAULT_STATE);
    }
    return parsed;
  } catch {
    return structuredClone(DEFAULT_STATE);
  }
}

export function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function getGeneration(genId) {
  const state = getState();
  return state.gens[genId] || null;
}

export function updateGeneration(genId, data) {
  const state = getState();
  state.gens[genId] = { ...state.gens[genId], ...data };
  saveState(state);
  return state;
}

export function updateGlobal(data) {
  const state = getState();
  state.global = { ...state.global, ...data };
  saveState(state);
  return state;
}

export function resetAll() {
  localStorage.removeItem(STORAGE_KEY);
}

export function getDefaultState() {
  return structuredClone(DEFAULT_STATE);
}
