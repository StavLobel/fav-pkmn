import 'package:flutter/material.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final headingStyle = theme.textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.bold,
    );
    final bodyStyle = theme.textTheme.bodyMedium?.copyWith(
      height: 1.6,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy Policy'),
        centerTitle: true,
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 700),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: SelectableText.rich(
              TextSpan(
                style: bodyStyle,
                children: [
                  TextSpan(
                    text: 'What We Collect\n',
                    style: headingStyle,
                  ),
                  const TextSpan(
                    text: 'PokePick does not collect any personal information. '
                        'We do not ask for your name, email address, or any '
                        'other identifying information. When you visit PokePick, '
                        'an anonymous voter token is generated and stored in a '
                        'browser cookie. This token is a random identifier with '
                        'no connection to your identity.\n\n',
                  ),
                  TextSpan(
                    text: 'Cookies\n',
                    style: headingStyle,
                  ),
                  const TextSpan(
                    text: 'PokePick uses a single secure, HttpOnly cookie to '
                        'store your anonymous voter token. This cookie exists '
                        'solely to prevent duplicate votes on the same daily '
                        'challenge. We do not use tracking cookies, analytics '
                        'cookies, or any third-party cookies.\n\n',
                  ),
                  TextSpan(
                    text: 'Third-Party Services\n',
                    style: headingStyle,
                  ),
                  const TextSpan(
                    text: 'Pokémon data and sprite images are fetched from '
                        'PokeAPI (pokeapi.co). No user data is sent to PokeAPI '
                        'or any other third-party service. PokePick does not '
                        'include any analytics, advertising, or tracking '
                        'services.\n\n',
                  ),
                  TextSpan(
                    text: 'Data Retention\n',
                    style: headingStyle,
                  ),
                  const TextSpan(
                    text: 'Votes are stored in our database with anonymous '
                        'tokens only. There is no way to identify individual '
                        'users from stored vote data. Vote records are retained '
                        'to display historical matchup results.\n\n',
                  ),
                  TextSpan(
                    text: 'Contact\n',
                    style: headingStyle,
                  ),
                  const TextSpan(
                    text: 'If you have questions or concerns about this privacy '
                        'policy, please open an issue on our GitHub repository '
                        'at github.com/StavLobel/fav-pkmn.',
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
