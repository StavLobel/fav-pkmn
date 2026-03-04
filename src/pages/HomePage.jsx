import { useState } from 'react';
import { useNavigate } from 'react-router';
import { GENERATIONS } from '../utils/generations';
import { useLocalStorage } from '../hooks/useLocalStorage';
import GenerationCard from '../components/GenerationCard';

export default function HomePage() {
  const navigate = useNavigate();
  const { state, reset } = useLocalStorage();
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  const allCompleted = GENERATIONS.every(
    (gen) => state.gens[gen.id]?.status === 'completed'
  );

  const completedCount = GENERATIONS.filter(
    (gen) => state.gens[gen.id]?.status === 'completed'
  ).length;

  function handleGenClick(gen) {
    const genState = state.gens[gen.id];
    if (genState?.status === 'completed') {
      navigate(`/result/${gen.id}`);
    } else {
      navigate(`/rank/${gen.id}`);
    }
  }

  function handleReset() {
    reset();
    setShowResetConfirm(false);
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-gray-800 mb-2">
            Favorite Pok&eacute;mon Ranker
          </h1>
          <p className="text-gray-500">
            Rank your favorites generation by generation, then crown your champion!
          </p>
          {completedCount > 0 && (
            <p className="text-sm text-gray-400 mt-2">
              {completedCount} of {GENERATIONS.length} generations completed
            </p>
          )}
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {GENERATIONS.map((gen) => (
            <GenerationCard
              key={gen.id}
              generation={gen}
              status={state.gens[gen.id]?.status || 'not_started'}
              onClick={handleGenClick}
            />
          ))}
        </div>

        <div className="flex flex-col items-center gap-4">
          {allCompleted && (
            <button
              data-testid="start-championship"
              onClick={() => navigate('/championship')}
              className="
                px-8 py-4 rounded-2xl font-bold text-lg text-white
                bg-gradient-to-r from-red-500 to-yellow-500
                shadow-lg shadow-red-200
                hover:scale-105 hover:shadow-xl transition-all duration-200
                active:scale-95
              "
            >
              Start Championship
            </button>
          )}

          {state.global?.status === 'completed' && (
            <button
              onClick={() => navigate('/championship/result')}
              className="
                px-6 py-3 rounded-xl font-semibold text-indigo-600
                bg-indigo-50 hover:bg-indigo-100 transition-colors
              "
            >
              View Global Top 10
            </button>
          )}

          {completedCount > 0 && (
            <div className="mt-4">
              {showResetConfirm ? (
                <div className="flex items-center gap-3 p-4 bg-red-50 rounded-xl">
                  <span className="text-sm text-red-600">Reset all progress?</span>
                  <button
                    data-testid="confirm-reset"
                    onClick={handleReset}
                    className="px-4 py-1.5 text-sm font-semibold text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Yes, Reset
                  </button>
                  <button
                    onClick={() => setShowResetConfirm(false)}
                    className="px-4 py-1.5 text-sm font-semibold text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  data-testid="reset-button"
                  onClick={() => setShowResetConfirm(true)}
                  className="text-sm text-gray-400 hover:text-red-500 transition-colors"
                >
                  Reset All Progress
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
