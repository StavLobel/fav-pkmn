# PokePick -- UI/UX Review

## Executive Summary

The Daily Starter frontend is a functional MVP built on Flutter Web with Material 3 and Provider. It correctly implements the core user flows from the SRS: viewing the daily matchup, casting a vote, seeing results, and browsing history. The architecture is clean -- models, providers, services, screens, and widgets are properly separated.

However, the current implementation is utilitarian. It relies almost entirely on default Material widgets with minimal customization, no animations beyond a single `AnimatedContainer`, no gamification hooks, and several accessibility gaps. The app does not yet feel like a daily ritual game. With targeted improvements to feedback loops, polish, and delight, this could become a sticky daily experience on par with the Wordle-like format it aspires to.

---

## Current State Analysis

### What the app does well

- **Clean separation of concerns.** The file structure (`models/`, `providers/`, `services/`, `screens/`, `widgets/`) follows the project's own conventions rule. The `MatchupProvider` centralizes all matchup and voting state, and `ApiService` is isolated and injectable.

- **Correct core flow.** The voting-to-results transition works: `DailyChallengeScreen` switches between `VotingView` and `ResultsView` based on `provider.hasVoted`, fulfilling FR-11 and FR-28.

- **Basic responsiveness.** `VotingView` uses `LayoutBuilder` to switch between a `Row` layout above 700px and a stacked `Column` below it. `ConstrainedBox(maxWidth: 900)` prevents the content from stretching on ultra-wide displays.

- **Error handling with retry.** Both `DailyChallengeScreen` and `HistoryScreen` show an error icon, message, and a `FilledButton` for retry. The provider handles 409 (duplicate vote) with a user-facing message.

- **Paginated history.** `HistoryScreen` implements infinite scroll with offset-based pagination, correctly loading more items when the sentinel widget appears.

- **Type-color mapping.** `PokemonCard._typeColors` maps all 18 Pokemon types to their canonical colors, which is a nice touch for fans.

### Where it falls short

- **No animation or transition layer.** The only animation is `AnimatedContainer` on `PokemonCard` selection. There are no page transitions, no results reveal, no vote submission feedback beyond a `CircularProgressIndicator`, and no celebration moment.

- **No micro-interactions.** `PokemonCard` uses `GestureDetector` instead of `InkWell` or a `Material` wrapper -- there is no ripple, no hover effect, and no press feedback. Cards feel inert.

- **No gamification.** There is no streak tracking, no countdown to the next matchup, no shareable result card. The app gives users no reason to return tomorrow.

- **Minimal visual identity.** The app uses a raw `ColorScheme.fromSeed` with `seedColor: Color(0xFFE94560)` and the default `Roboto` font. There is no custom typography, no logo, no brand presence beyond the title text in the `AppBar`.

- **Incomplete `index.html`.** No favicon, no Open Graph tags, no Apple touch icon, no themed status bar color. The page title is static and never updates to reflect the current state.

- **Accessibility gaps.** `Image.network` calls lack `semanticLabel`. `GestureDetector` does not expose an accessibility role. No `Semantics` widgets. Keyboard navigation is not supported on the voting cards.

---

## Recommendations

### HIGH PRIORITY

---

#### H1: Replace GestureDetector with InkWell and add hover/press effects on PokemonCard

**Current behavior:** `PokemonCard` wraps its content in a `GestureDetector`, which provides no visual feedback on tap, hover, or focus. On desktop browsers, the cursor does not change to a pointer.

**Suggested improvement:** Replace `GestureDetector` with an `InkWell` wrapped inside a `Material` widget (to provide the ink splash surface). Add a `MouseRegion` or rely on `InkWell`'s built-in hover callback to apply a subtle scale or elevation change on hover. Use `AnimatedScale` or `Transform.scale` for a press effect.

**Rationale:** Tap feedback is the single most basic UX expectation on the web. Without it, cards feel broken. This is especially noticeable on desktop where hover states are standard.

**Implementation notes:**

```dart
Material(
  color: Colors.transparent,
  borderRadius: BorderRadius.circular(20),
  child: InkWell(
    borderRadius: BorderRadius.circular(20),
    onTap: enabled ? onTap : null,
    hoverColor: theme.colorScheme.primary.withAlpha(20),
    splashColor: theme.colorScheme.primary.withAlpha(40),
    child: AnimatedContainer(
      // ...existing container code...
    ),
  ),
)
```

For a press-down scale effect, convert `PokemonCard` to a `StatefulWidget` and use `GestureDetector.onTapDown`/`onTapUp` with `AnimatedScale`:

```dart
AnimatedScale(
  scale: _isPressed ? 0.96 : 1.0,
  duration: const Duration(milliseconds: 100),
  child: // ...card content...
)
```

**Affected files:** `frontend/lib/widgets/pokemon_card.dart`

---

#### H2: Add a vote submission animation and results reveal

**Current behavior:** When the user taps a Pokemon, `provider.isSubmitting` becomes true and a `CircularProgressIndicator` appears below the cards. When voting completes, the screen instantly switches from `VotingView` to `ResultsView` with no transition.

**Suggested improvement:** Implement a multi-stage transition:

1. On tap, the selected card pulses or glows (confirm selection).
2. The non-selected cards fade out or slide away.
3. The results view fades/slides in with a staggered animation -- bars grow from 0% to their final width.
4. The winner indicator (crown/badge) appears with a small bounce or pop.

**Rationale:** The vote moment is the emotional peak of the app. An abrupt swap from voting to results feels anticlimactic and leaves users unsure if their vote registered.

**Implementation notes:**

Use `AnimatedSwitcher` in `DailyChallengeScreen` to crossfade between `VotingView` and `ResultsView`:

```dart
AnimatedSwitcher(
  duration: const Duration(milliseconds: 400),
  switchInCurve: Curves.easeOut,
  switchOutCurve: Curves.easeIn,
  child: provider.hasVoted
      ? ResultsView(key: const ValueKey('results'), ...)
      : VotingView(key: const ValueKey('voting'), ...),
)
```

For the progress bar animation in `ResultsView`, convert `_ResultCard` to a `StatefulWidget` and use an `AnimationController` with `CurvedAnimation` to tween the `LinearProgressIndicator.value` from 0 to the final percentage. Stagger using `Interval` offsets per card index.

Alternatively, use the `TweenAnimationBuilder` widget for a simpler approach:

```dart
TweenAnimationBuilder<double>(
  tween: Tween(begin: 0, end: result.votePercentage / 100),
  duration: const Duration(milliseconds: 800),
  curve: Curves.easeOutCubic,
  builder: (context, value, _) => LinearProgressIndicator(value: value, ...),
)
```

**Affected files:** `frontend/lib/screens/daily_challenge_screen.dart`, `frontend/lib/widgets/results_view.dart`, `frontend/lib/widgets/voting_view.dart`

---

#### H3: Add a "VS" divider between Pokemon cards in the voting view

**Current behavior:** The three Pokemon cards are laid out in a `Row` (desktop) or `Column` (mobile) with only `Padding` separating them. There is no visual cue that this is a competition.

**Suggested improvement:** Insert a styled "VS" badge between each pair of cards. On desktop (Row layout), this appears as a circular badge between cards. On mobile (Column layout), it appears as a horizontally-centered badge between stacked cards.

**Rationale:** The "versus" framing is core to the app's identity. Without it, the three cards look like a list, not a contest. This is a low-effort, high-impact visual change.

**Implementation notes:**

```dart
Widget _vsBadge(ThemeData theme) {
  return Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      color: theme.colorScheme.tertiaryContainer,
    ),
    child: Text(
      'VS',
      style: theme.textTheme.labelLarge?.copyWith(
        fontWeight: FontWeight.w900,
        color: theme.colorScheme.onTertiaryContainer,
        letterSpacing: 1,
      ),
    ),
  );
}
```

Interleave this between the mapped Pokemon cards in both the `Row` and `Column` branches of the `LayoutBuilder`.

**Affected files:** `frontend/lib/widgets/voting_view.dart`

---

#### H4: Add accessibility semantics and keyboard navigation

**Current behavior:** `Image.network` calls have no `semanticLabel`. `PokemonCard` uses `GestureDetector`, which does not produce a focusable, labeled semantic node. Screen readers cannot identify what each card represents. Keyboard users cannot tab between cards.

**Suggested improvement:**

1. Add `semanticLabel` to all `Image.network` widgets: `semanticLabel: '${pokemon.name} sprite'`.
2. Wrap each `PokemonCard` in a `Semantics` widget with `label`, `button: true`, and `enabled`.
3. If using `InkWell` (see H1), it already supports focus and keyboard activation via Enter/Space. Add `focusColor` and `autofocus` on the first card.
4. Add `Semantics(header: true)` around the "Who's your favorite?" heading.

**Rationale:** Accessibility is not optional for a public web app. Screen reader support and keyboard navigation are baseline requirements.

**Implementation notes:**

```dart
Semantics(
  label: '${_capitalize(pokemon.name)}, ${pokemon.types.join(' and ')} type. Tap to vote.',
  button: true,
  enabled: enabled,
  child: // ...InkWell + card content...
)
```

For results cards:

```dart
Semantics(
  label: '${_capitalize(result.name)}: ${result.voteCount} votes, '
      '${result.votePercentage} percent. '
      '${result.isWinner ? "Winner." : ""} '
      '${isUserPick ? "Your pick." : ""}',
  child: // ...card content...
)
```

**Affected files:** `frontend/lib/widgets/pokemon_card.dart`, `frontend/lib/widgets/results_view.dart`, `frontend/lib/screens/history_screen.dart`

---

#### H5: Add countdown timer to next daily challenge

**Current behavior:** After voting, the results screen is static. There is no indication of when the next matchup will be available. Users have no reason to return.

**Suggested improvement:** Display a countdown timer below the results that shows "Next challenge in HH:MM:SS", counting down to midnight (or whatever the configured reset time is). When the timer reaches zero, automatically reload the matchup or show a "New challenge available!" button.

**Rationale:** This is the single most important gamification hook for daily challenge games. Wordle, Connections, and every successful daily game shows this. It creates anticipation and establishes a return loop.

**Implementation notes:**

Create a `CountdownTimer` widget as a `StatefulWidget`:

```dart
class CountdownTimer extends StatefulWidget {
  const CountdownTimer({super.key, required this.onComplete});
  final VoidCallback onComplete;

  @override
  State<CountdownTimer> createState() => _CountdownTimerState();
}

class _CountdownTimerState extends State<CountdownTimer> {
  late Timer _timer;
  Duration _remaining = Duration.zero;

  @override
  void initState() {
    super.initState();
    _computeRemaining();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      _computeRemaining();
      if (_remaining <= Duration.zero) {
        _timer.cancel();
        widget.onComplete();
      }
    });
  }

  void _computeRemaining() {
    final now = DateTime.now();
    final midnight = DateTime(now.year, now.month, now.day + 1);
    setState(() => _remaining = midnight.difference(now));
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final hours = _remaining.inHours.toString().padLeft(2, '0');
    final minutes = (_remaining.inMinutes % 60).toString().padLeft(2, '0');
    final seconds = (_remaining.inSeconds % 60).toString().padLeft(2, '0');
    // Render with a monospace style: "$hours:$minutes:$seconds"
  }
}
```

Place this at the bottom of `ResultsView`. Use the `intl` package (already a dependency) if you need timezone-aware formatting.

**Affected files:** New file `frontend/lib/widgets/countdown_timer.dart`, `frontend/lib/widgets/results_view.dart`

---

#### H6: Implement share results (Wordle-style)

**Current behavior:** There is no way to share results. After voting, the experience is a dead end.

**Suggested improvement:** Add a "Share" button on the results screen that copies a text-based result card to the clipboard (similar to Wordle's colored grid). The format should include the date, the matchup, and a visual representation:

```
Daily Starter -- Mar 8, 2026

Bulbasaur  ████████░░ 42%
Charmander ██████████ 55%  <-- my pick
Squirtle   █░░░░░░░░░  3%

dailystarter.app
```

**Rationale:** Social sharing is the primary growth mechanism for daily challenge games. Wordle's iconic colored grid drove massive organic adoption. Sharing also reinforces the daily habit loop.

**Implementation notes:**

Use `Clipboard.setData` from `dart:services` to copy the text. Construct the share string from the `VoteResults` data. After copying, show a `SnackBar` confirming the copy.

```dart
import 'package:flutter/services.dart';

Future<void> _shareResults(VoteResults results, int? userPick) async {
  final buffer = StringBuffer('Daily Starter\n\n');
  for (final p in results.pokemon) {
    final bar = _buildBar(p.votePercentage);
    final pick = p.pokemonId == userPick ? '  <--' : '';
    buffer.writeln('${_capitalize(p.name).padRight(12)} $bar ${p.votePercentage.round()}%$pick');
  }
  await Clipboard.setData(ClipboardData(text: buffer.toString()));
}

String _buildBar(double pct) {
  final filled = (pct / 10).round();
  return '${'█' * filled}${'░' * (10 - filled)}';
}
```

Add a `FilledButton.icon(icon: Icon(Icons.share), label: Text('Share'))` to the bottom of `ResultsView`.

**Affected files:** `frontend/lib/widgets/results_view.dart`

---

### MEDIUM PRIORITY

---

#### M1: Replace the bare CircularProgressIndicator with skeleton loading

**Current behavior:** Both `DailyChallengeScreen` (loading matchup) and `HistoryScreen` (initial load) show a centered `CircularProgressIndicator`. This is a blank screen with a spinner -- the worst loading UX pattern.

**Suggested improvement:** Show skeleton placeholder cards that approximate the shape of the final content. For the voting view, show two or three card-shaped gray boxes with pulsing shimmer. For history, show several card outlines.

**Rationale:** Skeleton screens reduce perceived loading time by giving users a preview of the layout. They signal progress better than a spinner and prevent layout shift when content arrives.

**Implementation notes:**

Add the `shimmer` package (`shimmer: ^3.0.0`) to `pubspec.yaml`, or implement a simple shimmer effect manually with `AnimationController` and `ShaderMask`:

```dart
class SkeletonCard extends StatelessWidget {
  const SkeletonCard({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Shimmer.fromColors(
      baseColor: theme.colorScheme.surfaceContainerHighest,
      highlightColor: theme.colorScheme.surfaceContainerLow,
      child: Container(
        height: 180,
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }
}
```

Replace the `CircularProgressIndicator` in `_buildBody` cases `idle` and `loading` with a row/column of `SkeletonCard` widgets matching the voting layout.

**Affected files:** `frontend/lib/screens/daily_challenge_screen.dart`, `frontend/lib/screens/history_screen.dart`, `frontend/pubspec.yaml`

---

#### M2: Add page transition animation between DailyChallengeScreen and HistoryScreen

**Current behavior:** `Navigator.pushNamed(context, '/history')` performs a default platform slide transition. On web, this is typically just a cut (no animation).

**Suggested improvement:** Define custom page routes with a fade + slide transition. Use `PageRouteBuilder` or override the theme's `pageTransitionsTheme`.

**Rationale:** On Flutter Web, the default `MaterialPageRoute` often produces no visible transition, making navigation feel jarring.

**Implementation notes:**

In `main.dart`, replace the `routes` map with `onGenerateRoute` to apply custom transitions:

```dart
onGenerateRoute: (settings) {
  final Widget page;
  switch (settings.name) {
    case '/history':
      page = const HistoryScreen();
    default:
      page = const DailyChallengeScreen();
  }
  return PageRouteBuilder(
    settings: settings,
    pageBuilder: (_, __, ___) => page,
    transitionsBuilder: (_, animation, __, child) {
      return FadeTransition(
        opacity: CurvedAnimation(parent: animation, curve: Curves.easeOut),
        child: child,
      );
    },
    transitionDuration: const Duration(milliseconds: 250),
  );
},
```

**Affected files:** `frontend/lib/main.dart`

---

#### M3: Improve the results view layout for desktop

**Current behavior:** `ResultsView` stacks `_ResultCard` widgets vertically in a `Column`. Each card stretches to the full constrained width (900px). On a wide desktop screen, this looks like a long narrow list with excessive horizontal space.

**Suggested improvement:** On wider screens, display results in a more engaging format:

1. Show the Pokemon side by side (or in a podium layout) with large sprites above their progress bars.
2. Make the winner card visually distinct -- larger sprite, golden glow, elevated position.
3. Below the cards, show a stacked horizontal bar chart comparing all three.

**Rationale:** The results screen is the payoff moment. It should feel like a reveal, not a report. Horizontal layouts make better use of desktop real estate and create a more dramatic comparison.

**Implementation notes:**

Use `LayoutBuilder` in `ResultsView` (same pattern as `VotingView`) to switch between a compact vertical layout on mobile and a horizontal "podium" layout on desktop. Consider placing the winner in the center with a slightly larger card.

For the bar comparison, a custom `CustomPainter` or a package like `fl_chart` (`fl_chart: ^0.70.0`) could render a clean horizontal bar chart. However, the simpler approach is to use wider `LinearProgressIndicator` widgets inside a fixed-width container.

**Affected files:** `frontend/lib/widgets/results_view.dart`

---

#### M4: Add a custom font pairing and improve typography hierarchy

**Current behavior:** The app uses the default `Roboto` font family with Material 3's default text theme. The only typographic customization is occasional `fontWeight: FontWeight.bold`. There is no visual distinction between the app brand and body content.

**Suggested improvement:**

1. Use a display/heading font for the app title and section headings (e.g., `Press Start 2P` for a retro game feel, or `Fredoka One` / `Outfit` for a friendly modern feel).
2. Keep `Roboto` or switch to `Inter` for body text.
3. Define the font in `ThemeData.textTheme` so it propagates consistently.

**Rationale:** Typography is the cheapest way to establish visual identity. The current app looks like a generic Material scaffold. A distinctive heading font would immediately communicate "this is a game."

**Implementation notes:**

Add `google_fonts: ^6.2.0` to `pubspec.yaml`:

```dart
import 'package:google_fonts/google_fonts.dart';

theme: ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: const Color(0xFFE94560),
    brightness: Brightness.dark,
  ),
  useMaterial3: true,
  textTheme: GoogleFonts.outfitTextTheme(
    ThemeData(brightness: Brightness.dark).textTheme,
  ).copyWith(
    headlineMedium: GoogleFonts.pressStart2p(fontSize: 20),
    // ...other overrides
  ),
),
```

Alternatively, bundle font files in `assets/fonts/` and declare them in `pubspec.yaml` to avoid runtime Google Fonts fetches.

**Affected files:** `frontend/lib/main.dart`, `frontend/pubspec.yaml`

---

#### M5: Add confetti or celebration animation on vote submission

**Current behavior:** After a successful vote, the view switches to results with no celebration.

**Suggested improvement:** Trigger a brief confetti or sparkle burst when the vote is confirmed. The animation should be short (1-2 seconds) and non-blocking.

**Rationale:** Positive reinforcement at the moment of action strengthens the daily habit loop. Even a small celebration moment makes the interaction memorable.

**Implementation notes:**

Add `confetti: ^0.7.0` to `pubspec.yaml`:

```dart
import 'package:confetti/confetti.dart';

// In DailyChallengeScreen or ResultsView:
late final ConfettiController _confettiController;

@override
void initState() {
  super.initState();
  _confettiController = ConfettiController(duration: const Duration(seconds: 2));
}

// When results first appear:
_confettiController.play();

// In the widget tree:
Stack(
  children: [
    // ...existing content...
    Align(
      alignment: Alignment.topCenter,
      child: ConfettiWidget(
        confettiController: _confettiController,
        blastDirectionality: BlastDirectionality.explosive,
        colors: const [Color(0xFFE94560), Color(0xFFFFD700), Color(0xFF6390F0)],
        numberOfParticles: 20,
      ),
    ),
  ],
)
```

**Affected files:** `frontend/lib/screens/daily_challenge_screen.dart`, `frontend/pubspec.yaml`

---

#### M6: Replace emoji crown with a proper icon/widget for the winner indicator

**Current behavior:** The winner is indicated with a `Text('👑')` widget positioned over the sprite in both `ResultsView` and `HistoryScreen`. Emoji rendering varies across browsers and operating systems -- on some platforms it renders as a flat icon, on others as a colorful emoji, and on some it may not render at all.

**Suggested improvement:** Replace the emoji with either:
1. A Material icon (`Icons.workspace_premium` or a custom SVG crown icon).
2. An `Image.asset` with a pixel-art crown sprite to match the Pokemon aesthetic.

**Rationale:** Emoji is not a reliable cross-platform rendering strategy. A controlled asset ensures consistent appearance.

**Implementation notes:**

```dart
// Option 1: Material icon with gold color
Positioned(
  top: -8,
  right: -8,
  child: Icon(
    Icons.workspace_premium,
    color: const Color(0xFFFFD700),
    size: 24,
    shadows: [
      Shadow(color: Colors.black54, blurRadius: 4),
    ],
  ),
)
```

**Affected files:** `frontend/lib/widgets/results_view.dart`, `frontend/lib/screens/history_screen.dart`

---

#### M7: Improve error state with illustrations and actionable messages

**Current behavior:** The error state in `DailyChallengeScreen` shows `Icons.error_outline`, a generic message ("Failed to load matchup: {statusCode}"), and a Retry button. The status code is exposed to the user, which is meaningless to them.

**Suggested improvement:**

1. Map known error codes to user-friendly messages (e.g., 503 = "We're updating things. Try again in a moment.", network error = "You appear to be offline.").
2. Add an illustration or a larger, friendlier icon (a confused Pokemon, or a stylized error graphic).
3. Differentiate between "no internet" and "server error" states.

**Rationale:** Showing raw status codes erodes user trust. Friendly, specific error messages reduce frustration and increase retry likelihood.

**Implementation notes:**

In `MatchupProvider`, parse exceptions into user-friendly categories:

```dart
} on ApiException catch (e) {
  _state = LoadingState.error;
  _errorMessage = switch (e.statusCode) {
    404 => 'No matchup found for today. Check back soon!',
    503 => 'We are updating. Try again in a moment.',
    _ => 'Something went wrong. Please try again.',
  };
} on SocketException {
  _state = LoadingState.error;
  _errorMessage = 'You appear to be offline. Check your connection.';
}
```

In the UI, increase the icon size and add a subtitle:

```dart
Icon(Icons.cloud_off, size: 64, color: theme.colorScheme.onSurfaceVariant),
```

**Affected files:** `frontend/lib/providers/matchup_provider.dart`, `frontend/lib/screens/daily_challenge_screen.dart`

---

#### M8: Add an "already voted" visual distinction when revisiting

**Current behavior:** When a user revisits after voting (FR-28), the app shows `ResultsView`. There is no message like "You already voted today" -- the results just appear, which may confuse users who forgot they voted.

**Suggested improvement:** When results are shown on revisit (not immediately after voting), display a subtle banner or chip: "You voted earlier today" or "You picked [Pokemon name]!" above the results.

**Rationale:** This confirms to the user that their vote was recorded and clarifies why they cannot vote again. It closes the information gap between "I just voted" and "I already voted."

**Implementation notes:**

Track whether results are being shown after a fresh vote or on revisit. `MatchupProvider` already has `hasVoted` from the API response. Add a `bool _justVoted = false` flag that is only true when `submitVote` succeeds. Pass this to `ResultsView` to conditionally render a banner:

```dart
if (!justVoted)
  Container(
    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    decoration: BoxDecoration(
      color: theme.colorScheme.tertiaryContainer,
      borderRadius: BorderRadius.circular(8),
    ),
    child: Text(
      'You voted earlier today!',
      style: theme.textTheme.bodyMedium?.copyWith(
        color: theme.colorScheme.onTertiaryContainer,
      ),
    ),
  ),
```

**Affected files:** `frontend/lib/providers/matchup_provider.dart`, `frontend/lib/widgets/results_view.dart`, `frontend/lib/screens/daily_challenge_screen.dart`

---

### LOW PRIORITY

---

#### L1: Add favicon, Apple touch icon, Open Graph meta tags, and themed splash

**Current behavior:** `web/index.html` has a minimal `<head>` with only `charset`, `viewport`, `description`, and `title`. There is no favicon, no Apple touch icon, no Open Graph / Twitter Card meta tags. The browser tab shows the default Flutter favicon (or none). Social media link previews show nothing.

**Suggested improvement:**

1. Design a simple favicon (a Pokeball or the app's initial "DS") and add it in multiple sizes.
2. Add Open Graph meta tags (`og:title`, `og:description`, `og:image`, `og:url`) and Twitter Card tags.
3. Add `theme-color` meta tag to match the app's primary color.
4. Add an Apple touch icon.
5. Replace the blank white Flutter loading screen with a styled splash matching the app's dark theme and primary color.

**Rationale:** These are table-stakes for any public web app. Missing favicons look unprofessional, and missing OG tags mean shared links look blank on social platforms -- directly undermining the share feature (H6).

**Implementation notes:**

```html
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="icons/favicon-16.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="theme-color" content="#E94560">
<meta property="og:title" content="Daily Starter - Pokemon Voting Challenge">
<meta property="og:description" content="Vote for your favorite Pokemon in today's daily challenge.">
<meta property="og:image" content="https://dailystarter.app/og-image.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

For the Flutter loading splash, style the `<body>` background and add a CSS-animated loader:

```html
<style>
  body { background: #1a1a2e; margin: 0; }
  .loading { /* centered spinner matching brand colors */ }
</style>
```

**Affected files:** `frontend/web/index.html`, new image assets in `frontend/web/icons/`

---

#### L2: Add a light mode toggle or system-preference detection

**Current behavior:** The app is hardcoded to `Brightness.dark` in `ThemeData`. There is no light mode and no way to switch.

**Suggested improvement:**

1. Define both a light and dark `ThemeData` using the same seed color.
2. Use `WidgetsBinding.instance.platformDispatcher.platformBrightness` to detect the system preference.
3. Optionally, add a toggle button (sun/moon icon) in the `AppBar` that saves the preference to `SharedPreferences`.

**Rationale:** Some users strongly prefer light mode, especially on mobile in bright environments. Supporting both themes with `ColorScheme.fromSeed` is low effort since Material 3 generates complementary light and dark palettes automatically.

**Implementation notes:**

```dart
MaterialApp(
  theme: ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFFE94560),
      brightness: Brightness.light,
    ),
    useMaterial3: true,
  ),
  darkTheme: ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFFE94560),
      brightness: Brightness.dark,
    ),
    useMaterial3: true,
  ),
  themeMode: ThemeMode.system, // or user preference
)
```

Add `shared_preferences: ^2.3.0` for persisting the choice.

**Affected files:** `frontend/lib/main.dart`, `frontend/pubspec.yaml`

---

#### L3: Add a second responsive breakpoint for tablet/medium screens

**Current behavior:** `VotingView` has a single 700px breakpoint. Below 700px, all three cards stack vertically. Above 700px, all three cards sit in a single row. There is no intermediate layout.

**Suggested improvement:** Add a middle breakpoint (around 500-700px) where two cards sit side-by-side with the third below, or use a `Wrap` widget to flow cards naturally. On very wide screens (>1100px), increase card sizes and spacing.

**Rationale:** On tablets in portrait mode (~768px), three cards in a row can feel cramped. The stacked layout wastes space. A wrap-based layout adapts gracefully to any width.

**Implementation notes:**

Replace the `LayoutBuilder` branching with a `Wrap` widget:

```dart
Wrap(
  alignment: WrapAlignment.center,
  spacing: 16,
  runSpacing: 16,
  children: pokemon.map((p) => SizedBox(
    width: constraints.maxWidth > 900 ? 260 : constraints.maxWidth > 500 ? 200 : double.infinity,
    child: PokemonCard(pokemon: p, ...),
  )).toList(),
)
```

This automatically reflows cards based on available space without manual breakpoint management.

**Affected files:** `frontend/lib/widgets/voting_view.dart`

---

#### L4: Improve history screen layout for wider screens

**Current behavior:** `HistoryScreen` renders a `ListView.builder` with `_HistoryCard` widgets. Each card shows the date, total votes, and the Pokemon sprites in a `Row`. On wide screens, the cards stretch edge-to-edge.

**Suggested improvement:**

1. Constrain the history list to a max width (e.g., 700px) centered on the screen, like the daily challenge screen does.
2. Consider a grid layout on wider screens: `SliverGrid` with 2 columns for history cards.
3. Add the vote percentage per Pokemon in the history card (currently only total votes are shown, not individual breakdowns).

**Rationale:** Unconstrained-width cards on wide screens look stretched and sparse. The lack of vote breakdown in history makes past matchups less interesting to review.

**Implementation notes:**

Wrap the `ListView` in a `Center` > `ConstrainedBox(maxWidth: 700)`:

```dart
body: Center(
  child: ConstrainedBox(
    constraints: const BoxConstraints(maxWidth: 700),
    child: // ...existing ListView...
  ),
),
```

**Affected files:** `frontend/lib/screens/history_screen.dart`

---

#### L5: Preload and cache Pokemon sprite images

**Current behavior:** `Image.network` is used directly in `PokemonCard`, `ResultsView`, and `HistoryScreen`. Each has an `errorBuilder` fallback, but there is no loading placeholder or pre-fetching.

**Suggested improvement:**

1. Add `loadingBuilder` to `Image.network` to show a placeholder while the sprite loads (a small `CircularProgressIndicator` or a gray box).
2. Use `cached_network_image: ^3.4.0` for disk-level caching so sprites don't re-download on revisits.
3. Call `precacheImage` in `initState` when the matchup loads to start downloading sprites before they're visible.

**Rationale:** Pokemon sprites from PokeAPI are small (~3-5KB each) so they usually load fast, but on slow connections or first visits, a missing sprite with no placeholder looks broken.

**Implementation notes:**

```dart
// Using cached_network_image:
CachedNetworkImage(
  imageUrl: pokemon.spriteUrl,
  height: 96,
  width: 96,
  fit: BoxFit.contain,
  filterQuality: FilterQuality.none,
  placeholder: (_, __) => SizedBox(
    height: 96,
    width: 96,
    child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
  ),
  errorWidget: (_, __, ___) => const SizedBox(
    height: 96,
    width: 96,
    child: Icon(Icons.catching_pokemon, size: 48),
  ),
)
```

Note: `cached_network_image` has a web-compatible version but relies on browser caching. For web, the simpler approach is to use `Image.network` with `loadingBuilder` and let HTTP cache headers handle reuse.

**Affected files:** `frontend/lib/widgets/pokemon_card.dart`, `frontend/lib/widgets/results_view.dart`, `frontend/lib/screens/history_screen.dart`, `frontend/pubspec.yaml`

---

#### L6: Add streak tracking display

**Current behavior:** There is no concept of streaks. Users have no way to know how many consecutive days they have voted.

**Suggested improvement:** Add a streak counter displayed in the `AppBar` or below the results. The streak could be tracked client-side via `SharedPreferences` (storing the last vote date and incrementing a counter). Display it as "Streak: 5 days" or with a flame icon.

**Rationale:** Streak mechanics are proven retention drivers. They give users a reason to return daily and create a small sense of loss aversion when the streak might break.

**Implementation notes:**

Since the backend does not track streaks (it's stateless/anonymous), this is a client-side feature:

```dart
// shared_preferences
final prefs = await SharedPreferences.getInstance();
final lastDate = prefs.getString('last_vote_date');
final streak = prefs.getInt('streak') ?? 0;
final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
final yesterday = DateFormat('yyyy-MM-dd').format(
    DateTime.now().subtract(const Duration(days: 1)));

if (lastDate == yesterday) {
  await prefs.setInt('streak', streak + 1);
} else if (lastDate != today) {
  await prefs.setInt('streak', 1);
}
await prefs.setString('last_vote_date', today);
```

Display in the AppBar:

```dart
actions: [
  Padding(
    padding: const EdgeInsets.symmetric(horizontal: 8),
    child: Row(
      children: [
        Icon(Icons.local_fire_department, color: Color(0xFFFF6B35), size: 20),
        const SizedBox(width: 4),
        Text('$streak'),
      ],
    ),
  ),
  // ...history button
],
```

**Affected files:** `frontend/lib/screens/daily_challenge_screen.dart`, `frontend/lib/providers/matchup_provider.dart`, `frontend/pubspec.yaml` (add `shared_preferences`)

---

#### L7: Eliminate the duplicated `_capitalize` helper

**Current behavior:** The static method `_capitalize(String s)` is defined independently in three files: `pokemon_card.dart` (line 114), `results_view.dart` (line 167), and `history_screen.dart` (line 195). All three have identical implementations.

**Suggested improvement:** Extract to a shared utility:

```dart
// lib/utils/string_utils.dart
String capitalize(String s) =>
    s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';
```

Alternatively, consider capitalizing the name at the model layer in `Pokemon.fromJson` so display code never needs to worry about casing.

**Rationale:** This is a minor code hygiene issue, not a UX problem per se. But it reflects a pattern where display logic is scattered across widgets instead of being centralized, which will slow down future UI changes.

**Affected files:** `frontend/lib/widgets/pokemon_card.dart`, `frontend/lib/widgets/results_view.dart`, `frontend/lib/screens/history_screen.dart`, new file `frontend/lib/utils/string_utils.dart`

---

#### L8: Update the page title dynamically

**Current behavior:** The browser tab always shows "Daily Starter" regardless of what screen the user is on.

**Suggested improvement:** Update `document.title` (via `dart:html` on web, or the `Title` widget) to reflect the current state:
- Voting: "Daily Starter -- Vote Now"
- Results: "Daily Starter -- Results"
- History: "Daily Starter -- History"

**Rationale:** Dynamic page titles help users with multiple tabs identify the app state at a glance and improve browser history readability.

**Implementation notes:**

Flutter's `Title` widget (from `package:flutter/widgets.dart`) updates the browser tab:

```dart
Title(
  title: 'Daily Starter - Vote Now',
  color: theme.colorScheme.primary,
  child: Scaffold(...),
)
```

**Affected files:** `frontend/lib/screens/daily_challenge_screen.dart`, `frontend/lib/screens/history_screen.dart`

---

#### L9: Add a "today" indicator and improved date formatting in history

**Current behavior:** `HistoryScreen` displays the raw `match_date` string (e.g., "2026-03-08") from the API. The format is ISO 8601, which is not user-friendly. There is no visual differentiation for today's entry versus past entries.

**Suggested improvement:**

1. Format dates using the `intl` package (already a dependency): "Mar 8, 2026" or "Today", "Yesterday", "Mar 6".
2. Highlight today's entry with a badge or different card color.
3. Add a relative time indicator for recent entries ("2 days ago").

**Implementation notes:**

```dart
import 'package:intl/intl.dart';

String formatMatchDate(String isoDate) {
  final date = DateTime.parse(isoDate);
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final yesterday = today.subtract(const Duration(days: 1));
  final parsed = DateTime(date.year, date.month, date.day);

  if (parsed == today) return 'Today';
  if (parsed == yesterday) return 'Yesterday';
  return DateFormat.yMMMd().format(date);
}
```

**Affected files:** `frontend/lib/screens/history_screen.dart`

---

## Implementation Roadmap

Suggested order of implementation, balancing impact and complexity:

| Order | Item | Priority | Complexity | Rationale |
|-------|------|----------|------------|-----------|
| 1 | H1: InkWell + hover/press effects | High | S | Fundamental interaction feedback; minimal code change |
| 2 | H3: VS divider between cards | High | S | Immediate visual impact, ~20 lines of code |
| 3 | H2: Vote animation + results reveal | High | M | Core UX improvement; requires AnimatedSwitcher and TweenAnimationBuilder |
| 4 | M6: Replace emoji crown with icon | Medium | S | One-line fix per file, eliminates cross-platform rendering issue |
| 5 | L7: Extract _capitalize to shared util | Low | S | Quick cleanup, no UX impact but reduces future maintenance friction |
| 6 | H4: Accessibility semantics + keyboard nav | High | M | Important for compliance; requires Semantics wrapping across multiple files |
| 7 | M1: Skeleton loading screens | Medium | M | Requires shimmer package or custom animation, applied in two screens |
| 8 | H5: Countdown timer | High | M | New widget, requires Timer and state management |
| 9 | M8: "Already voted" banner on revisit | Medium | S | Small provider flag + conditional UI |
| 10 | M7: Improved error messages | Medium | S | String mapping in provider, minor UI tweaks |
| 11 | H6: Share results | High | M | String construction + clipboard API |
| 12 | M5: Confetti on vote | Medium | S | Package integration, ~15 lines |
| 13 | M4: Custom font pairing | Medium | S | google_fonts package or bundled assets |
| 14 | M2: Page transition animation | Medium | S | PageRouteBuilder in main.dart |
| 15 | L1: Favicon + OG tags + splash | Low | M | Asset creation + HTML edits |
| 16 | L4: History screen max-width constraint | Low | S | 3-line wrapper |
| 17 | L9: Date formatting in history | Low | S | Uses existing intl dependency |
| 18 | L8: Dynamic page titles | Low | S | Title widget wrapping |
| 19 | M3: Desktop results layout | Medium | L | Layout rework with LayoutBuilder, possible podium design |
| 20 | L3: Additional responsive breakpoints | Low | M | Wrap-based layout redesign |
| 21 | L5: Image preloading + cached_network_image | Low | M | Package integration, touching three files |
| 22 | L2: Light mode toggle | Low | M | Dual theme definition, SharedPreferences, toggle UI |
| 23 | L6: Streak tracking | Low | L | SharedPreferences, date logic, AppBar integration, edge case handling |

**Complexity key:** S = a few hours or less, M = half a day to a full day, L = 1-2 days, XL = multiple days.

Items 1-5 can be shipped as a single "interaction polish" PR. Items 6-10 form a "usability" batch. Items 11-14 are the "gamification and identity" batch. The remainder are incremental improvements that can be picked up opportunistically.
