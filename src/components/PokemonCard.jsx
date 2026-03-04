import { getPokemonSpriteUrl } from '../hooks/usePokemon';

export default function PokemonCard({ pokemon, onClick, selected, size = 'md' }) {
  const spriteUrl = pokemon?.sprite || getPokemonSpriteUrl(pokemon?.id);
  const name = pokemon?.name || `#${pokemon?.id}`;

  const sizeClasses = {
    sm: 'w-24 p-2',
    md: 'w-36 p-3',
    lg: 'w-44 p-4',
  };

  return (
    <button
      data-testid="pokemon-card"
      onClick={() => onClick?.(pokemon)}
      className={`
        ${sizeClasses[size] || sizeClasses.md}
        flex flex-col items-center rounded-2xl bg-white shadow-md
        transition-all duration-200 ease-out
        hover:scale-105 hover:shadow-xl hover:-translate-y-1
        active:scale-95
        ${selected ? 'ring-4 ring-yellow-400 shadow-yellow-200/50' : ''}
        ${onClick ? 'cursor-pointer' : 'cursor-default'}
      `}
    >
      <img
        data-testid="pokemon-sprite"
        src={spriteUrl}
        alt={name}
        className="w-full aspect-square object-contain"
        loading="lazy"
      />
      <span
        data-testid="pokemon-name"
        className="mt-1 text-sm font-semibold capitalize text-gray-700 truncate w-full text-center"
      >
        {name}
      </span>
    </button>
  );
}
