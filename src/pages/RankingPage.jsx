import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router';
import { getGeneration, getGenPokemonIds, getGenSize } from '../utils/generations';
import { shuffleArray, createGroups, recordSelection, buildCandidatePool, getNextPair, checkStability, getTopN, isMaxComparisonsReached } from '../utils/ranking';
import { updateRatings } from '../utils/elo';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { usePokemonBatch } from '../hooks/usePokemon';
import PokemonCard from '../components/PokemonCard';
import ProgressBar from '../components/ProgressBar';

export default function RankingPage() {
  const { genId } = useParams();
  const navigate = useNavigate();
  const { state, updateGen } = useLocalStorage();
  const gen = getGeneration(genId);

  const [phase, setPhase] = useState('discovery');
  const [groups, setGroups] = useState([]);
  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);
  const [scores, setScores] = useState({});

  const [candidatePool, setCandidatePool] = useState([]);
  const [ratings, setRatings] = useState({});
  const [comparisons, setComparisons] = useState({});
  const [ratingHistory, setRatingHistory] = useState([]);
  const [totalComparisons, setTotalComparisons] = useState(0);
  const [currentPair, setCurrentPair] = useState(null);

  useEffect(() => {
    if (!gen) return;

    const saved = state.gens[genId];

    if (saved?.status === 'completed') {
      navigate(`/result/${genId}`, { replace: true });
      return;
    }

    if (saved?.phase === 'pairwise') {
      setPhase('pairwise');
      setCandidatePool(saved.candidatePool || []);
      setRatings(saved.ratings || {});
      setComparisons(saved.comparisons || {});
      setRatingHistory(saved.ratingHistory || []);
      setTotalComparisons(saved.totalComparisons || 0);
    } else if (saved?.phase === 'discovery') {
      setPhase('discovery');
      setGroups(saved.groups || []);
      setCurrentGroupIndex(saved.currentIndex || 0);
      setScores(saved.scores || {});
    } else {
      initDiscovery();
    }
  }, [genId]);

  useEffect(() => {
    if (phase === 'pairwise' && candidatePool.length > 0 && !currentPair) {
      const pair = getNextPair(candidatePool, ratings, comparisons);
      setCurrentPair(pair);
    }
  }, [phase, candidatePool, ratings, comparisons, currentPair]);

  function initDiscovery() {
    const ids = getGenPokemonIds(genId);
    const shuffled = shuffleArray(ids);
    const grouped = createGroups(shuffled);
    setGroups(grouped);
    setCurrentGroupIndex(0);
    setScores({});
    setPhase('discovery');

    updateGen(genId, {
      status: 'in_progress',
      phase: 'discovery',
      groups: grouped,
      currentIndex: 0,
      scores: {},
    });
  }

  function handleDiscoverySelect(pokemon) {
    const newScores = recordSelection(scores, pokemon.id);
    setScores(newScores);

    const nextIndex = currentGroupIndex + 1;

    if (nextIndex >= groups.length) {
      const genSize = getGenSize(genId);
      const pool = buildCandidatePool(newScores, genSize);
      const initialRatings = {};
      pool.forEach((id) => {
        initialRatings[id] = 1500;
      });

      setCandidatePool(pool);
      setRatings(initialRatings);
      setComparisons({});
      setRatingHistory([]);
      setTotalComparisons(0);
      setCurrentPair(null);
      setPhase('pairwise');

      updateGen(genId, {
        status: 'in_progress',
        phase: 'pairwise',
        candidatePool: pool,
        ratings: initialRatings,
        comparisons: {},
        ratingHistory: [],
        totalComparisons: 0,
        scores: newScores,
      });
    } else {
      setCurrentGroupIndex(nextIndex);
      updateGen(genId, {
        status: 'in_progress',
        phase: 'discovery',
        groups,
        currentIndex: nextIndex,
        scores: newScores,
      });
    }
  }

  function handlePairwiseSelect(pokemon) {
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
      updateGen(genId, {
        status: 'completed',
        phase: 'completed',
        top10,
        candidatePool,
        ratings: newRatings,
      });
      navigate(`/result/${genId}`, { replace: true });
    } else {
      updateGen(genId, {
        status: 'in_progress',
        phase: 'pairwise',
        candidatePool,
        ratings: newRatings,
        comparisons: newComparisons,
        ratingHistory: newHistory,
        totalComparisons: newTotal,
      });
    }
  }

  const visibleIds = useMemo(() => {
    if (phase === 'discovery' && groups[currentGroupIndex]) {
      return groups[currentGroupIndex];
    }
    if (phase === 'pairwise' && currentPair) {
      return currentPair;
    }
    return [];
  }, [phase, groups, currentGroupIndex, currentPair]);

  const { dataMap, loading } = usePokemonBatch(visibleIds);

  if (!gen) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-red-50 to-blue-50">
        <p className="text-gray-500 text-lg">Generation not found.</p>
      </div>
    );
  }

  const maxComparisons = candidatePool.length * 5;

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">
            Gen {gen.id} — {gen.name}
          </h1>
          <p className="text-gray-500 mt-1">
            {phase === 'discovery' ? 'Pick your favorite from each group' : 'Who do you prefer?'}
          </p>
        </header>

        <div className="mb-6">
          {phase === 'discovery' ? (
            <ProgressBar
              current={currentGroupIndex}
              total={groups.length}
              label="Discovery Progress"
            />
          ) : (
            <ProgressBar
              current={totalComparisons}
              total={maxComparisons}
              label="Ranking Progress"
            />
          )}
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className={`flex justify-center gap-4 flex-wrap ${phase === 'pairwise' ? 'gap-8' : ''}`}>
            {visibleIds.map((id) => {
              const pokemon = dataMap[id] || { id, name: `#${id}` };
              return (
                <PokemonCard
                  key={id}
                  pokemon={pokemon}
                  onClick={phase === 'discovery' ? handleDiscoverySelect : handlePairwiseSelect}
                  size={phase === 'pairwise' ? 'lg' : 'md'}
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
