# 🚀 本番環境デプロイガイド

このガイドは、野球打球分析アプリケーションを本番環境で稼働させるための手順です。

---

## 📋 前提条件

### ローカル/開発環境
- Python 3.11 以上
- pip または poetry

### 本番環境（サーバー）
- **Docker による稼働**（推奨）
  - Docker & Docker Compose がインストール済み
  - ポート 8501 が開放可能
  
- **systemd による稼働**
  - Debian/Ubuntu/CentOS などの Linux
  - systemd サービス対応

### Supabase セットアップ
- Supabase プロジェクト が作成済み
- `batting_data` テーブルが作成済み
- サービスキー（`SUPABASE_SERVICE_KEY`）を取得済み

---

## 🔒 セキュリティ注意事項

**❌ 絶対にしないこと:**
- `.env` ファイルを Git にコミットする
- Supabase サービスキーをリポジトリに平文で記載する
- `.streamlit/secrets.toml` に機密情報を直接書き込む

**✅ 推奨される方法:**
- `.env` ファイルは**ローカルと各サーバーにのみ配置**
- CI/CD では GitHub Secrets を使用
- サーバーでは `/etc/default/streamlit_<username>` に環境変数を配置

---

## 🐳 Docker による本番デプロイ

### ステップ 1: リポジトリをクローン

```bash
git clone https://github.com/ryotashimogaki0205-ai/baseball-analysis-of-batter.git
cd baseball-analysis-of-batter
```

### ステップ 2: `.env` ファイルを作成

リポジトリルートに `.env` を作成し、以下を記載します（`.gitignore` に自動で除外されます）：

```bash
cat > .env <<EOF
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_publishable_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data
EOF
```

### ステップ 3: Docker イメージをビルドして起動

```bash
docker compose up -d --build
```

### ステップ 4: 稼働状況を確認

```bash
# ログを確認
docker compose logs -f

# コンテナが起動しているか確認
docker compose ps
```

### ステップ 5: ブラウザからアクセス

```
http://localhost:8501
```

---

## 🔧 systemd による本番デプロイ（サーバー）

### ステップ 1: リポジトリをクローン

```bash
git clone https://github.com/ryotashimogaki0205-ai/baseball-analysis-of-batter.git
cd baseball-analysis-of-batter
```

### ステップ 2: 依存関係をインストール

```bash
pip3 install -r requirements.txt
```

### ステップ 3: 環境変数ファイルを作成

サーバー上で `/etc/default/streamlit_<username>` を作成します（例：`streamlit_app`）：

```bash
sudo tee /etc/default/streamlit_app > /dev/null <<EOF
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_publishable_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data
HOME=/home/app
USER=app
EOF

sudo chmod 600 /etc/default/streamlit_app
```

### ステップ 4: systemd ユニットファイルを設置

```bash
sudo cp deployment/streamlit.service /etc/systemd/system/streamlit@.service
sudo systemctl daemon-reload
```

### ステップ 5: サービスを有効化・起動

```bash
# 特定ユーザー（app）で起動する場合
sudo systemctl enable streamlit@app.service
sudo systemctl start streamlit@app.service

# 起動確認
sudo systemctl status streamlit@app.service

# ログ確認
sudo journalctl -u streamlit@app.service -f
```

---

## 🧪 動作確認

### ローカル環境で動作確認

```bash
# 依存関係インストール
pip install -r requirements.txt

# Streamlit 起動
streamlit run app.py
```

### 本番環境での動作確認

```bash
# ブラウザで確認
http://<server-ip>:8501

# ロードバランサーを通す場合
http://<domain-name>
```

---

## 📝 トラブルシューティング

### ❌ コンテナが起動しない

```bash
# ログを確認
docker compose logs baseball-analysis-app

# .env ファイルの存在確認
ls -la .env

# Supabase 接続確認
docker compose exec streamlit-app python -c "from supabase import create_client; print('OK')"
```

### ❌ Supabase に接続できない

```bash
# 環境変数が正しくセットされているか確認
docker compose exec streamlit-app env | grep SUPABASE
```

### ❌ ポート 8501 が既に使用中

```bash
# 別のポートを使用（docker-compose.yml を修正）
ports:
  - "8502:8501"  # ホストの 8502 を使用
```

---

## 🔐 本番環境でのセキュリティベストプラクティス

### 1. ファイアウォール設定

```bash
# Streamlit は内部ネットワークのみに公開
sudo ufw allow from 192.168.0.0/16 to any port 8501

# または、ロードバランサー経由でのみアクセス可能にする
```

### 2. HTTPS/SSL 設定

```bash
# Nginx を使った HTTPS リバースプロキシの例
# (別途 Nginx 設定が必要)
```

### 3. 定期バックアップ

```bash
# Supabase 側でバックアップを有効化
# (Supabase ダッシュボードで設定)
```

### 4. ログ監視

```bash
# systemd の場合
sudo journalctl -u streamlit@app.service --since today

# Docker の場合
docker compose logs --tail 100
```

---

## 📚 関連ドキュメント

- [DEPLOY.md](./DEPLOY.md) - デプロイ基本手順
- [deployment/README.md](./deployment/README.md) - デプロイスクリプト説明
- [Dockerfile](./Dockerfile) - コンテナイメージ定義
- [docker-compose.yml](./docker-compose.yml) - Docker Compose 設定

---

## ❓ よくある質問

**Q: サービスキーを置き忘れた場合？**
A: サーバーにアクセスして `/etc/default/streamlit_<username>` を編集し、新しいサービスキーを記載してください。その後 `sudo systemctl restart streamlit@<username>.service` で再起動します。

**Q: アプリをアップデートしたい場合？**
A: `git pull` で最新コードを取得後、`docker compose up -d --build` または `sudo systemctl restart streamlit@<username>.service` で再起動します。

**Q: ポート 8501 を変更したい場合？**
A: `docker-compose.yml` の `ports` を変更するか、Nginx などのリバースプロキシを設定してください。

---

📧 問題が発生した場合は、GitHub Issues で報告してください。

