import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { GENERATIONS } from '../utils/generations';
import { getNextPair, checkStability, getTopN, isMaxComparisonsReached } from '../utils/ranking';
import { updateRatings } from '../utils/elo';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { usePokemonBatch } from '../hooks/usePokemon';
import PokemonCard from '../components/PokemonCard';
import ProgressBar from '../components/ProgressBar';

export default function ChampionshipPage() {
  const navigate = useNavigate();
  const { state, updateGlobal } = useLocalStorage();

  const [candidatePool, setCandidatePool] = useState([]);
  const [ratings, setRatings] = useState({});
  const [comparisons, setComparisons] = useState({});
  const [ratingHistory, setRatingHistory] = useState([]);
  const [totalComparisons, setTotalComparisons] = useState(0);
  const [currentPair, setCurrentPair] = useState(null);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (state.global?.status === 'completed' && state.global?.top10) {
      navigate('/championship/result', { replace: true });
      return;
    }

    if (state.global?.status === 'in_progress') {
      setCandidatePool(state.global.candidatePool || []);
      setRatings(state.global.ratings || {});
      setComparisons(state.global.comparisons || {});
      setRatingHistory(state.global.ratingHistory || []);
      setTotalComparisons(state.global.totalComparisons || 0);
      setInitialized(true);
      return;
    }

    const allPool = [];
    const initialRatings = {};

    GENERATIONS.forEach((gen) => {
      const genState = state.gens[gen.id];
      if (genState?.status === 'completed' && genState.top10) {
        genState.top10.forEach((pokemon) => {
          allPool.push(pokemon.id);
          initialRatings[pokemon.id] = 1500;
        });
      }
    });

    if (allPool.length === 0) {
      navigate('/', { replace: true });
      return;
    }

    setCandidatePool(allPool);
    setRatings(initialRatings);
    setComparisons({});
    setRatingHistory([]);
    setTotalComparisons(0);
    setInitialized(true);

    updateGlobal({
      status: 'in_progress',
      candidatePool: allPool,
      ratings: initialRatings,
      comparisons: {},
      ratingHistory: [],
      totalComparisons: 0,
    });
  }, []);

  useEffect(() => {
    if (initialized && candidatePool.length > 0 && !currentPair) {
      const pair = getNextPair(candidatePool, ratings, comparisons);
      setCurrentPair(pair);
    }
  }, [initialized, candidatePool, ratings, comparisons, currentPair]);

  const visibleIds = useMemo(() => {
    return currentPair || [];
  }, [currentPair]);

  const { dataMap, loading } = usePokemonBatch(visibleIds);

  function handleSelect(pokemon) {
    if (!currentPair) return;

    const winnerId = pokemon.id;
    const loserId = currentPair.find((id) => id !== winnerId);

    const winnerRating = ratings[winnerId] || 1500;
    const loserRating = ratings[loserId] || 1500;
    const { newWinnerRating, newLoserRating } = updateRatings(winnerRating, loserRating);

    const ratingChange = Math.abs(newWinnerRating - winnerRating);
    const newRatings = { ...ratings, [winnerId]: newWinnerRating, [loserId]: newLoserRating };
    const newHistory = [...ratingHistory, ratingChange];
    const pKey = `${Math.min(winnerId, loserId)}-${Math.max(winnerId, loserId)}`;
    const newComparisons = { ...comparisons, [pKey]: (comparisons[pKey] || 0) + 1 };
    const newTotal = totalComparisons + 1;

    setRatings(newRatings);
    setRatingHistory(newHistory);
    setComparisons(newComparisons);
    setTotalComparisons(newTotal);
    setCurrentPair(null);

    const stable = checkStability(newHistory);
    const maxReached = isMaxComparisonsReached(newTotal, candidatePool.length);

    if (stable || maxReached) {
      const top10 = getTopN(newRatings);
      updateGlobal({
        status: 'completed',
        top10,
        candidatePool,
        ratings: newRatings,
      });
      navigate('/championship/result', { replace: true });
    } else {
      updateGlobal({
        status: 'in_progress',
        candidatePool,
        ratings: newRatings,
        comparisons: newComparisons,
        ratingHistory: newHistory,
        totalComparisons: newTotal,
      });
    }
  }

  const maxComparisons = candidatePool.length * 5;

  if (!initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-red-50 to-blue-50">
        <div className="w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-red-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Championship</h1>
          <p className="text-gray-500 mt-1">
            The best from every generation compete — who do you prefer?
          </p>
        </header>

        <div className="mb-6">
          <ProgressBar
            current={totalComparisons}
            total={maxComparisons}
            label="Championship Progress"
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="w-10 h-10 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="flex justify-center gap-8 flex-wrap">
            {visibleIds.map((id) => {
              const pokemon = dataMap[id] || { id, name: `#${id}` };
              return (
                <PokemonCard
                  key={id}
                  pokemon={pokemon}
                  onClick={handleSelect}
                  size="lg"
                />
              );
            })}
          </div>
        )}

        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
