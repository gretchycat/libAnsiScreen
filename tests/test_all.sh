#!/bin/bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Running full test suite via pytest..."
PYTHONPATH="$PROJECT_DIR/src" pytest "$SCRIPT_DIR"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\033[1;32m=== All unit tests passed! Outputs generated in tests/out/ ===\033[0m"
else
    echo -e "\033[1;31m=== Test suite failed with exit code $EXIT_CODE ===\033[0m"
fi

exit $EXIT_CODE
