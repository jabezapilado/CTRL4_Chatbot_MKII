from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from server.service import get_chatbot_service  # noqa: E402


def main() -> int:
    service = get_chatbot_service()

    if service.initialization_error:
        print(service.initialization_error)
        return 1

    count = service.build_index()
    print(f"Indexed chunks: {count}")
    print(f"Docs directory: {service.docs_dir}")
    print(f"Index directory: {service.index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
