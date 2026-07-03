from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from server.services import rag_service  # noqa: E402


def main() -> int:

    if rag_service.initialization_error:

        print(rag_service.initialization_error)

        return 1

    count = rag_service.build_index()

    print("=" * 60)
    print("CTRL4 RAG INDEX BUILDER")
    print("=" * 60)

    print(f"Indexed chunks : {count}")

    print(f"Documents      : {rag_service.docs_dir}")

    print(f"Index          : {rag_service.index_dir}")

    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())