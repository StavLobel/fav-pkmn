import { useParams, useNavigate } from 'react-router';
import { getGeneration } from '../utils/generations';
import { useLocalStorage } from '../hooks/useLocalStorage';
import TopList from '../components/TopList';

export default function ResultPage() {
  const { genId } = useParams();
  const navigate = useNavigate();
  const { state, updateGen } = useLocalStorage();

  const gen = getGeneration(genId);
  const genState = state.gens[genId];

  if (!gen || !genState?.top10) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-red-50 to-blue-50">
        <p className="text-gray-500 text-lg mb-4">No results yet for this generation.</p>
        <button
          onClick={() => navigate(`/rank/${genId}`)}
          className="px-6 py-2 rounded-xl font-semibold text-white bg-blue-500 hover:bg-blue-600 transition-colors"
        >
          Start Ranking
        </button>
      </div>
    );
  }

  function handleRefine() {
    updateGen(genId, {
      status: 'in_progress',
      phase: 'pairwise',
      top10: null,
      totalComparisons: 0,
      ratingHistory: [],
      comparisons: {},
    });
    navigate(`/rank/${genId}`);
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-blue-50">
      <div className="max-w-lg mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Gen {gen.id} — {gen.name}
          </h1>
          <p className="text-gray-500 mt-1">Your Top 10</p>
        </header>

        <TopList rankings={genState.top10} />

        <div className="flex flex-col items-center gap-3 mt-8">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 rounded-xl font-semibold text-white bg-blue-500 hover:bg-blue-600 transition-colors shadow-md"
          >
            Back to Home
          </button>
          <button
            data-testid="refine-ranking"
            onClick={handleRefine}
            className="px-6 py-2 rounded-xl font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
          >
            Refine Ranking
          </button>
        </div>
      </div>
    </div>
  );
}
