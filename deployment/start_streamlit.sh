#!/usr/bin/env bash
set -euo pipefail
# 起動スクリプト: 仮想環境をアクティベートして Streamlit をフォアグラウンドで実行します

BASE_DIR="/workspaces/baseball-analysis-of-batter"
VENV_DIR="$BASE_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
  # POSIX sh 互換で venv をアクティベート
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
fi

cd "$BASE_DIR"

# ログ出力先
mkdir -p "$BASE_DIR/logs"
exec streamlit run app.py --server.port 8501 --server.address 0.0.0.0 2>&1 | tee -a "$BASE_DIR/logs/streamlit.log"
