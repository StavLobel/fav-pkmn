export default function ProgressBar({ current, total, label }) {
  const pct = total > 0 ? Math.min((current / total) * 100, 100) : 0;

  return (
    <div data-testid="progress-bar" className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-600">{label}</span>
          <span className="text-sm text-gray-400">
            {current}/{total}
          </span>
        </div>
      )}
      <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          data-testid="progress-bar-fill"
          className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
