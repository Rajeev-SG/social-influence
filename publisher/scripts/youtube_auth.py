#!/usr/bin/env python3
"""YouTube OAuth bootstrap (one-time, then refresh tokens do the rest).

Runs a local redirect server and prints the consent URL. Complete consent in
the brands.sgill@gmail.com Chrome profile (the URL is opened there manually or
by the caller), Google redirects to localhost, tokens are exchanged and saved
to $SOCIAL_INFLUENCE_STATE_DIR/google_token.json.

Usage:  .venv/bin/python scripts/youtube_auth.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from social_influence.providers.base import state_dir  # noqa: E402


def main() -> int:
    from google_auth_oauthlib.flow import InstalledAppFlow

    client = state_dir() / "google_oauth_client.json"
    if not client.exists():
        print(f"missing {client}", file=sys.stderr)
        return 1
    from social_influence.providers.youtube import SCOPES

    flow = InstalledAppFlow.from_client_secrets_file(str(client), SCOPES)
    # bind to a fixed loopback port; redirect_uri is registered dynamically
    creds = flow.run_local_server(
        port=8791,
        open_browser=False,
        success_message="YouTube auth complete — you can close this tab.",
    )
    token = state_dir() / "google_token.json"
    token.write_text(creds.to_json())
    print(f"saved tokens -> {token}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())