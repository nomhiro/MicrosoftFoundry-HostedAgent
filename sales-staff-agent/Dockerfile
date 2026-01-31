# 販売店スタッフエージェント Dockerfile
# Python 3.11 ベースイメージ

FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# uv のインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルをコピー
COPY pyproject.toml .

# 依存関係のインストール
RUN uv sync --no-dev

# アプリケーションコードをコピー
COPY src/ ./src/
COPY agent.yaml .

# Hosting Adapter のデフォルトポート
EXPOSE 8088

# エントリーポイント
CMD ["uv", "run", "python", "src/container.py"]
