import { useState, useEffect, useRef } from 'react';

const SPRITE_BASE =
  'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon';

const cache = new Map();

export function getPokemonSpriteUrl(id) {
  return `${SPRITE_BASE}/${id}.png`;
}

export function usePokemon(id) {
  const [data, setData] = useState(() => cache.get(id) || null);
  const [loading, setLoading] = useState(!cache.has(id));
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    if (!id) return;

    if (cache.has(id)) {
      setData(cache.get(id));
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    fetch(`https://pokeapi.co/api/v2/pokemon/${id}`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch Pokemon #${id}`);
        return res.json();
      })
      .then((json) => {
        const pokemon = {
          id: json.id,
          name: json.name,
          sprite: json.sprites.front_default || getPokemonSpriteUrl(id),
        };
        cache.set(id, pokemon);
        setData(pokemon);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [id]);

  return { data, loading, error };
}

export function usePokemonBatch(ids) {
  const [dataMap, setDataMap] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ids || ids.length === 0) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    const promises = ids.map((id) => {
      if (cache.has(id)) {
        return Promise.resolve(cache.get(id));
      }
      return fetch(`https://pokeapi.co/api/v2/pokemon/${id}`)
        .then((res) => {
          if (!res.ok) throw new Error(`Failed to fetch Pokemon #${id}`);
          return res.json();
        })
        .then((json) => {
          const pokemon = {
            id: json.id,
            name: json.name,
            sprite: json.sprites.front_default || getPokemonSpriteUrl(id),
          };
          cache.set(id, pokemon);
          return pokemon;
        })
        .catch(() => ({
          id,
          name: `Pokemon #${id}`,
          sprite: getPokemonSpriteUrl(id),
        }));
    });

    Promise.all(promises).then((results) => {
      if (cancelled) return;
      const map = {};
      results.forEach((p) => {
        map[p.id] = p;
      });
      setDataMap(map);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [ids?.join(',')]);

  return { dataMap, loading };
}
