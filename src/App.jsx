import { Routes, Route } from 'react-router';
import HomePage from './pages/HomePage';
import RankingPage from './pages/RankingPage';
import ResultPage from './pages/ResultPage';
import ChampionshipPage from './pages/ChampionshipPage';
import GlobalResultPage from './pages/GlobalResultPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/rank/:genId" element={<RankingPage />} />
      <Route path="/result/:genId" element={<ResultPage />} />
      <Route path="/championship" element={<ChampionshipPage />} />
      <Route path="/championship/result" element={<GlobalResultPage />} />
    </Routes>
  );
}
