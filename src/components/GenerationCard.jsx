import { getPokemonSpriteUrl } from '../hooks/usePokemon';

const STATUS_STYLES = {
  not_started: { label: 'Not Started', bg: 'bg-gray-100', text: 'text-gray-500', ring: '' },
  in_progress: { label: 'In Progress', bg: 'bg-amber-100', text: 'text-amber-700', ring: 'ring-2 ring-amber-300' },
  completed: { label: 'Completed', bg: 'bg-emerald-100', text: 'text-emerald-700', ring: 'ring-2 ring-emerald-300' },
};

export default function GenerationCard({ generation, status, onClick }) {
  const statusInfo = STATUS_STYLES[status] || STATUS_STYLES.not_started;
  const starterIds = generation.starterIds || [generation.startId, generation.startId + 3, generation.startId + 6];

  return (
    <button
      data-testid="generation-card"
      onClick={() => onClick?.(generation)}
      className={`
        relative flex flex-col items-center p-5 rounded-2xl bg-white shadow-md
        transition-all duration-200 ease-out w-full
        hover:scale-[1.03] hover:shadow-xl hover:-translate-y-1
        active:scale-[0.98]
        ${statusInfo.ring}
      `}
    >
      <div className="flex gap-1 mb-3">
        {starterIds.map((id) => (
          <img
            key={id}
            src={getPokemonSpriteUrl(id)}
            alt=""
            className="w-12 h-12 object-contain"
            loading="lazy"
          />
        ))}
      </div>

      <h3 className="text-lg font-bold text-gray-800">
        Gen {generation.id} — {generation.name}
      </h3>

      <p className="text-xs text-gray-400 mt-0.5">
        #{generation.startId}–#{generation.endId}
      </p>

      <span
        data-testid="gen-status-badge"
        className={`
          mt-3 px-3 py-1 rounded-full text-xs font-semibold
          ${statusInfo.bg} ${statusInfo.text}
        `}
      >
        {statusInfo.label}
      </span>
    </button>
  );
}
