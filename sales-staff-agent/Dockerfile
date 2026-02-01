# 販売店スタッフエージェント Dockerfile
# Python 3.11 ベースイメージ
# Microsoft Foundry Hosted Agent 対応

FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# uv のインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock* ./

# 依存関係のインストール（プレリリース版を許可）
RUN uv sync --no-dev --prerelease=allow

# アプリケーションコードをコピー
COPY src/ ./src/

# Hosted Agent のデフォルトポート
EXPOSE 8088

# エントリーポイント
CMD ["uv", "run", "python", "src/container.py"]
