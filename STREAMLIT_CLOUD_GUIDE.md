# 🚀 Streamlit Community Cloud での公開ガイド

無料で 1 分で公開できます。

---

## 📋 前提条件

- GitHub アカウント
- Supabase プロジェクトの公開キーとサービスキー

---

## ✨ 公開手順（5 分で完了）

### 1️⃣ Streamlit Community Cloud にアクセス

ブラウザで以下を開く：

```
https://streamlit.io/cloud
```

### 2️⃣ GitHub でサインイン

「**Sign in with GitHub**」をクリック

### 3️⃣ アプリをデプロイ

1. ページ左上の「**New app**」をクリック
2. 以下を選択：
   - **Repository:** `ryotashimogaki0205-ai/baseball-analysis-of-batter`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. 「**Deploy**」をクリック

### 4️⃣ デプロイ完了

自動ビルドされ、**2-3 分後**にアプリが公開されます。

URL 例：`https://baseball-analysis-of-batter-<random>.streamlit.app`

---

## 🔐 Supabase シークレットを設定

### ステップ 1: Settings を開く

デプロイ後、**アプリ右上 → Settings**

### ステップ 2: Secrets を開く

左メニュー → **Secrets**

### ステップ 3: シークレットを追加

以下の TOML 形式で入力：

```toml
[supabase]
url = "https://your-project-id.supabase.co"
key = "your_publishable_key_here"
service_key = "your_service_key_here"

[supabase]
table_name = "batting_data"
```

**値の取得方法：**

1. Supabase ダッシュボードにログイン
2. **Settings → API**
3. 以下をコピー：
   - `Project URL` → `url`
   - `Project API Key (public, anon)` → `key`
   - `Service Role Secret Key` → `service_key`

### ステップ 4: アプリが再起動

設定後、自動で再起動されます。

---

## ✅ 動作確認

ブラウザでアプリにアクセス → Supabase に接続できたか確認

---

## 🔄 自動更新

GitHub にコミットをプッシュすると、**自動で再デプロイ**されます。

```bash
git push origin main  # 自動デプロイ開始
```

---

## 📱 URL をシェア

公開 URL をそのままシェア可能：

```
https://baseball-analysis-of-batter-<random>.streamlit.app
```

---

## 🎯 次のステップ

- アプリをテスト
- URL を他の人とシェア
- 本番環境への設定を完了

---

## ❓ よくある問題

### ❌ 「Module not found」エラー

`requirements.txt` に依存パッケージが記載されているか確認。

### ❌ Supabase に接続できない

- シークレットの値が正しいか確認
- Settings → Secrets で再度確認
- アプリを再起動（Reboot button）

### ❌ URL にアクセスできない

デプロイ中の場合があります。2-3 分待ってから再度アクセスしてください。

---

## 📞 その他のデプロイ方法

- **Docker:** `docker compose up -d --build`
- **Linux サーバー:** `systemctl start streamlit@app`
- **Heroku:** [詳細ガイド](https://docs.streamlit.io/deploy/tutorials/deploy-streamlit-heroku)

---

**🎉 これで公開完了です！**

