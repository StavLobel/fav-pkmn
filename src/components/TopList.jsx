import { getPokemonSpriteUrl, usePokemonBatch } from '../hooks/usePokemon';

const RANK_COLORS = [
  'from-yellow-400 to-amber-500',
  'from-gray-300 to-gray-400',
  'from-orange-300 to-orange-400',
];

export default function TopList({ rankings, title }) {
  const ids = rankings.map((r) => r.id);
  const { dataMap, loading } = usePokemonBatch(ids);

  return (
    <div data-testid="top-list" className="w-full max-w-md mx-auto">
      {title && (
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">{title}</h2>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <ol className="space-y-2">
          {rankings.map((entry, index) => {
            const pokemon = dataMap[entry.id];
            const name = pokemon?.name || `Pokemon #${entry.id}`;
            const isTop3 = index < 3;

            return (
              <li
                key={entry.id}
                data-testid="top-list-item"
                className={`
                  flex items-center gap-3 p-3 rounded-xl
                  ${isTop3 ? 'bg-gradient-to-r ' + RANK_COLORS[index] + ' text-white shadow-lg' : 'bg-white shadow-sm'}
                  transition-all duration-200
                `}
              >
                <span
                  className={`
                    w-8 h-8 flex items-center justify-center rounded-full font-bold text-sm
                    ${isTop3 ? 'bg-white/30' : 'bg-gray-100 text-gray-600'}
                  `}
                >
                  {index + 1}
                </span>

                <img
                  src={pokemon?.sprite || getPokemonSpriteUrl(entry.id)}
                  alt={name}
                  className="w-12 h-12 object-contain"
                />

                <span className={`flex-1 font-semibold capitalize ${isTop3 ? '' : 'text-gray-700'}`}>
                  {name}
                </span>

                <span className={`text-sm font-mono ${isTop3 ? 'text-white/80' : 'text-gray-400'}`}>
                  {Math.round(entry.rating)}
                </span>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
