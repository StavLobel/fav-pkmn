export function calculateExpectedScore(ratingA, ratingB) {
  return 1 / (1 + Math.pow(10, (ratingB - ratingA) / 400));
}

export function updateRatings(winnerRating, loserRating, K = 32) {
  const expectedWin = calculateExpectedScore(winnerRating, loserRating);
  const expectedLose = calculateExpectedScore(loserRating, winnerRating);

  const newWinnerRating = Math.round(winnerRating + K * (1 - expectedWin));
  const newLoserRating = Math.round(loserRating + K * (0 - expectedLose));

  return { newWinnerRating, newLoserRating };
}
