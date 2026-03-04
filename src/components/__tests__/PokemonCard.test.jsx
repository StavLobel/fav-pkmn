import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import PokemonCard from '../PokemonCard';

vi.mock('../../hooks/usePokemon', () => ({
  getPokemonSpriteUrl: (id) => `https://sprites/${id}.png`,
}));

describe('PokemonCard', () => {
  const pokemon = {
    id: 25,
    name: 'pikachu',
    sprite: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png',
  };

  it('CT-PC-01: renders name and sprite', () => {
    render(<PokemonCard pokemon={pokemon} onClick={() => {}} />);

    expect(screen.getByTestId('pokemon-name')).toHaveTextContent(/pikachu/i);

    const img = screen.getByTestId('pokemon-sprite');
    expect(img).toHaveAttribute('src', pokemon.sprite);
  });

  it('CT-PC-02: calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<PokemonCard pokemon={pokemon} onClick={handleClick} />);

    fireEvent.click(screen.getByTestId('pokemon-card'));
    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(handleClick).toHaveBeenCalledWith(pokemon);
  });

  it('CT-PC-03: shows loading state', () => {
    render(<PokemonCard pokemon={pokemon} loading={true} />);

    const card = screen.getByTestId('pokemon-card');
    expect(card).toBeInTheDocument();
  });
});
