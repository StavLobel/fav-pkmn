import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import GenerationCard from '../GenerationCard';

vi.mock('../../hooks/usePokemon', () => ({
  getPokemonSpriteUrl: (id) => `https://sprites/${id}.png`,
}));

describe('GenerationCard', () => {
  const generation = { id: 1, name: 'Kanto', startId: 1, endId: 151 };

  it('CT-GC-01: renders generation name', () => {
    render(<GenerationCard generation={generation} status="not_started" onClick={() => {}} />);
    const card = screen.getByTestId('generation-card');
    expect(card).toHaveTextContent(/Gen 1/i);
    expect(card).toHaveTextContent(/Kanto/i);
  });

  it('CT-GC-02: shows not started status', () => {
    render(<GenerationCard generation={generation} status="not_started" onClick={() => {}} />);
    const badge = screen.getByTestId('gen-status-badge');
    expect(badge).toHaveTextContent(/not started/i);
  });

  it('CT-GC-03: shows in progress status', () => {
    render(<GenerationCard generation={generation} status="in_progress" onClick={() => {}} />);
    const badge = screen.getByTestId('gen-status-badge');
    expect(badge).toHaveTextContent(/in progress/i);
  });

  it('CT-GC-04: shows completed status', () => {
    render(<GenerationCard generation={generation} status="completed" onClick={() => {}} />);
    const badge = screen.getByTestId('gen-status-badge');
    expect(badge).toHaveTextContent(/completed/i);
  });

  it('CT-GC-05: click navigates to ranking', () => {
    const handleClick = vi.fn();
    render(<GenerationCard generation={generation} status="not_started" onClick={handleClick} />);

    fireEvent.click(screen.getByTestId('generation-card'));
    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(handleClick).toHaveBeenCalledWith(generation);
  });
});
