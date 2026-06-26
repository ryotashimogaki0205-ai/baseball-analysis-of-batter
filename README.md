# ⚾ 野球打球分析アプリケーション

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)

野球の打球データを分析・可視化するための Streamlit アプリケーション。Supabase をバックエンドとして利用し、安全かつスケーラブルなデータ管理を実現します。

---

## 🎯 主な機能

- 📊 **打球データの可視化** - Plotly を使用した高度なチャート
- 💾 **データ管理** - Supabase によるセキュアなデータベース
- 🔒 **セキュアな認証** - 環境変数による安全な設定管理
- 🐳 **コンテナ化** - Docker による簡単デプロイ
- 🖥️ **systemd 対応** - Linux サーバーでの常時稼働

---

## 🚀 クイックスタート

### ローカル環境（開発）

#### 1. リポジトリをクローン

```bash
git clone https://github.com/ryotashimogaki0205-ai/baseball-analysis-of-batter.git
cd baseball-analysis-of-batter
```

#### 2. Python 仮想環境を作成

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

#### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

#### 4. 環境変数を設定

リポジトリルートに `.env` ファイルを作成：

```bash
cat > .env <<EOF
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_publishable_key
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_TABLE=batting_data
EOF
```

#### 5. アプリを起動

```bash
streamlit run app.py
```

ブラウザが自動で開き、アプリが表示されます: http://localhost:8501

---

## 🐳 Docker での実行（推奨）

### 1 コマンドで起動：

```bash
# .env ファイルを作成してから実行
docker compose up -d --build
```

ブラウザで http://localhost:8501 にアクセス

---

## 📦 本番環境へのデプロイ

### Docker Compose でのデプロイ
```bash
docker compose up -d --build
```

### systemd でのデプロイ（Linux サーバー）
```bash
sudo systemctl enable streamlit@app.service
sudo systemctl start streamlit@app.service
```

詳細な手順は [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) を参照してください。

---

## 📋 システム要件

### ローカル開発
- Python 3.11 以上
- pip または poetry
- 512 MB RAM 以上

### 本番環境（Docker）
- Docker & Docker Compose
- 1 GB RAM 以上
- 10 GB ディスク容量

### 本番環境（systemd）
- Debian/Ubuntu または CentOS 7 以上
- Python 3.11 以上
- 2 GB RAM 以上

---

## 🔐 セキュリティ

- ✅ サービスキーは `.env` または `/etc/default/` に配置（Git から除外）
- ✅ 環境変数を使用した安全な設定管理
- ✅ `.gitignore` で機密ファイルを自動除外
- ✅ Supabase の認証と権限管理

**⚠️ 重要:** `.env` ファイルや `/etc/default/streamlit_*` ファイルを公開リポジトリにコミットしないでください。

---

## 📊 プロジェクト構成

```
.
├── app.py                      # メイン Streamlit アプリケーション
├── requirements.txt            # Python 依存パッケージ
├── Dockerfile                  # Docker イメージ定義
├── docker-compose.yml          # Docker Compose 設定
├── DEPLOY.md                   # 基本デプロイ手順
├── DEPLOYMENT_GUIDE.md         # 詳細な本番デプロイガイド
├── deployment/
│   ├── streamlit.service       # systemd サービスファイル
│   ├── start_streamlit.sh      # 起動スクリプト
│   └── README.md               # デプロイスクリプト説明
├── scripts/
│   └── create_supabase_table.py # Supabase テーブル作成スクリプト
└── .streamlit/
    └── secrets.toml            # Streamlit ローカルシークレット

```

---

## 🛠️ 技術スタック

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11 | 言語 |
| Streamlit | 最新 | UI フレームワーク |
| Pandas | 最新 | データ処理 |
| Plotly | 最新 | データ可視化 |
| Supabase | - | バックエンド DB |
| Docker | - | コンテナ化 |

---

## 📖 ドキュメント

| ファイル | 説明 |
|---------|------|
| [DEPLOY.md](./DEPLOY.md) | クイック 3 ステップデプロイ |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 本番環境の詳細ガイド |
| [deployment/README.md](./deployment/README.md) | デプロイスクリプト説明 |

---

## 🐛 トラブルシューティング

### Streamlit が起動しない

```bash
# ポート 8501 が使用中の場合
streamlit run app.py --server.port 8502

# ログを詳細表示
streamlit run app.py --logger.level=debug
```

### Supabase に接続できない

```bash
# .env ファイルを確認
cat .env

# 環境変数を確認
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

詳細は [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#-トラブルシューティング) を参照。

---

## 🤝 貢献

バグ報告や機能提案は GitHub Issues でお願いします。

---

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

---

## 👨‍💻 開発者向け情報

### 開発環境でのセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/ryotashimogaki0205-ai/baseball-analysis-of-batter.git

# 仮想環境を作成
python -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# アプリを起動
streamlit run app.py
```

### コード スタイル

- Python 3.11 以上の最新機能を使用
- PEP 8 に準拠
- 型ヒント を推奨

---

## 📞 サポート

問題が発生した場合は以下をご確認ください：

1. [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) のトラブルシューティング
2. GitHub Issues で類似の問題を検索
3. 新しく Issue を作成（可能な限り詳細に）

---

**最終更新:** 2026-06-26

