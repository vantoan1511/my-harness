#!/usr/bin/env bash
# my-harness installer for Linux / macOS
set -e

COMMAND="init"
DRY_RUN=""
SCOPE=""
TARGET=""
PACK=""

# Parse arguments
while [ "$#" -gt 0 ]; do
    case "$1" in
        fix|init)
            COMMAND="$1"
            shift
            ;;
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        -s|--scope)
            SCOPE="$2"
            shift 2
            ;;
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -p|--pack)
            PACK="$2"
            shift 2
            ;;
        *)
            if [ -z "$TARGET" ]; then
                TARGET="$1"
            elif [ -z "$PACK" ]; then
                PACK="$1"
            fi
            shift
            ;;
    esac
done

TARGET="${TARGET:-.}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_PY="$SCRIPT_DIR/harness.py"

if [ ! -f "$HARNESS_PY" ]; then
    echo "Error: harness.py not found at $HARNESS_PY" >&2
    exit 1
fi

if [ "$COMMAND" = "fix" ]; then
    ARGS=("$HARNESS_PY" "fix" "$TARGET")
    if [ -n "$DRY_RUN" ]; then
        ARGS+=("$DRY_RUN")
    fi
else
    # Prompt user interactively if scope is not specified and running in interactive terminal
    if [ -z "$SCOPE" ]; then
        if [ -t 0 ]; then
            echo ""
            echo "========================================================"
            echo " my-harness Installer - Choose Installation Scope"
            echo "========================================================"
            echo "  1) Project (Default) - Install .agents in project directory ($TARGET)"
            echo "  2) Global            - Install .agents in ~/.agents and register 'harness' CLI"
            echo "  3) Fix               - Repair project .agents and deduplicate global items"
            echo "--------------------------------------------------------"
            read -r -p "Select option [1/2/3] (default: 1): " CHOICE
            if [ "$CHOICE" = "2" ] || [ "$CHOICE" = "global" ]; then
                SCOPE="global"
            elif [ "$CHOICE" = "3" ] || [ "$CHOICE" = "fix" ]; then
                COMMAND="fix"
                ARGS=("$HARNESS_PY" "fix" "$TARGET")
            else
                SCOPE="project"
            fi
        else
            SCOPE="project"
        fi
    fi

    if [ "$COMMAND" != "fix" ]; then
        ARGS=("$HARNESS_PY" "init")
        if [ "$SCOPE" = "global" ]; then
            ARGS+=("--scope" "global")
        else
            ARGS+=("$TARGET" "--scope" "project")
        fi

        if [ -n "$PACK" ]; then
            ARGS+=("--pack" "$PACK")
        fi
    fi
fi

if command -v python3 >/dev/null 2>&1 && python3 -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1 && python -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Error: Python 3 not found. Please ensure Python is installed and in your PATH." >&2
    exit 1
fi

"$PYTHON_BIN" "${ARGS[@]}"
