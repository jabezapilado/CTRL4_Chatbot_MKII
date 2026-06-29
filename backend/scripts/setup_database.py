from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from server.db import initialize_database, list_accounts  # noqa: E402


def main() -> int:
    initialize_database()
    accounts = list_accounts()

    print("Database initialized successfully.")
    print(f"Seeded accounts: {len(accounts)}")
    for account in accounts:
        print(f"- {account['email']} ({account['role']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())