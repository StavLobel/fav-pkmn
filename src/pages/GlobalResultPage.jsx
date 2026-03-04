import { useNavigate } from 'react-router';
import { useLocalStorage } from '../hooks/useLocalStorage';
import TopList from '../components/TopList';

export default function GlobalResultPage() {
  const navigate = useNavigate();
  const { state } = useLocalStorage();

  if (!state.global?.top10) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-yellow-50 to-red-50">
        <p className="text-gray-500 text-lg mb-4">No championship results yet.</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2 rounded-xl font-semibold text-white bg-blue-500 hover:bg-blue-600 transition-colors"
        >
          Go Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-red-50">
      <div className="max-w-lg mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Your Top 10 Pok&eacute;mon
          </h1>
          <p className="text-gray-500 mt-1">
            Champions from across all generations
          </p>
        </header>

        <TopList rankings={state.global.top10} title="Global Champions" />

        <div className="flex flex-col items-center gap-3 mt-8">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 rounded-xl font-semibold text-white bg-blue-500 hover:bg-blue-600 transition-colors shadow-md"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
