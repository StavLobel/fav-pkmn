import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import TopList from '../TopList';

vi.mock('../../hooks/usePokemon', () => ({
  getPokemonSpriteUrl: (id) => `https://sprites/${id}.png`,
  usePokemonBatch: (ids) => ({
    dataMap: Object.fromEntries(
      ids.map((id) => [
        id,
        { id, name: `pokemon-${id}`, sprite: `https://sprites/${id}.png` },
      ])
    ),
    loading: false,
  }),
}));

const mockRankings = Array.from({ length: 10 }, (_, i) => ({
  id: i + 1,
  name: `pokemon-${i + 1}`,
  rating: 1600 - i * 15,
}));

describe('TopList', () => {
  it('CT-TL-01: renders 10 ranked items', () => {
    render(<TopList rankings={mockRankings} />);

    const items = screen.getAllByTestId('top-list-item');
    expect(items).toHaveLength(10);
  });

  it('CT-TL-02: displays names and sprites', () => {
    render(<TopList rankings={mockRankings} />);

    const items = screen.getAllByTestId('top-list-item');
    items.forEach((item) => {
      expect(item.querySelector('img')).toBeInTheDocument();
      expect(item).toHaveTextContent(/pokemon-/);
    });
  });

  it('CT-TL-03: items ordered by rank', () => {
    render(<TopList rankings={mockRankings} />);

    const items = screen.getAllByTestId('top-list-item');
    expect(items[0]).toHaveTextContent('pokemon-1');
    expect(items[9]).toHaveTextContent('pokemon-10');
  });
});
