手順: セキュアな方法でアプリを常時稼働させる

## 超かんたん3ステップ
1. `.env`というファイルを作る
2. その中にSupabaseのURL・公開キー・サービスキー・テーブル名を入れる
3. `docker compose up -d --build` を実行してアプリを起動する

前提
- サーバーに docker / docker-compose または systemd が利用可能であること
- Supabase プロジェクトの `SUPABASE_SERVICE_KEY`（管理キー）を安全にサーバーに配置できること

推奨フロー（Docker）
1. リポジトリルートに `.env` を作成し、以下を記載します（このファイルは `.gitignore` に登録済みです）:

SUPABASE_URL=https://hpzpkdyvjlvpfzbeddax.supabase.co
SUPABASE_KEY=sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data

2. Docker を利用して起動します:

```bash
docker compose up -d --build
# もしくは
# docker-compose up -d --build
```

3. コンテナログを確認します:

```bash
docker compose logs -f
```

systemd フロー（server）
1. サーバー上で `/etc/default/streamlit_<username>` を作成し、以下を記載します:

SUPABASE_URL=https://hpzpkdyvjlvpfzbeddax.supabase.co
SUPABASE_KEY=sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data

2. ユニットファイルを配置して有効化します:

```bash
sudo cp deployment/streamlit.service /etc/systemd/system/streamlit@.service
sudo systemctl daemon-reload
sudo systemctl enable --now streamlit@<username>.service
sudo journalctl -u streamlit@<username>.service -f
```

Supabase にテーブルが無い場合
- 最速の解決は Supabase ダッシュボードの SQL エディタで以下 SQL を実行することです:

```sql
CREATE TABLE IF NOT EXISTS public.batting_data (
  id serial PRIMARY KEY,
  team_name text,
  player_name text,
  plate_id text,
  course text,
  pitch_type text,
  catch_position text,
  batted_ball_angle double precision,
  pitcher_hand text,
  count text,
  result text,
  input_datetime timestamp with time zone
);
```

注意（セキュリティ）
- サービスキーは絶対にリポジトリに平文でコミットしないでください。`.env` や `/etc/default` にのみ配置してください。
- もし私にサーバー上で操作を代行してほしい場合は、限定的な SSH 鍵と実行ユーザー、必要な権限（sudo 権限の有無）を教えてください。安全性のため、鍵は一時的・限定的にしてください。

**自動化で行った変更と手順（詳細）**

- **変更概要**: 私が実行した自動化／修正は、機密情報の除去・安全な参照方法への切替・デプロイ設定の整備・テーブル作成の試行です。

- **主な変更ファイル**:
  - [.streamlit/secrets.toml](.streamlit/secrets.toml): サービスキーを空にして平文を削除しました（ローカル専用にしてください）。
  - [docker-compose.yml](docker-compose.yml): `env_file: .env` を使うようにし、環境変数を `${VAR}` 参照に置き換えました。
  - [deployment/streamlit.service](deployment/streamlit.service): ユニットファイルから平文環境変数を除去し、`EnvironmentFile=/etc/default/streamlit_%i` を使うよう変更しました。
  - [.gitignore](.gitignore): `.env` と `.streamlit/secrets.toml` を無視リストに追加しました。
  - [scripts/create_supabase_table.py](scripts/create_supabase_table.py): Supabase の `run_sql` RPC を使ってテーブル作成を試行するスクリプトを追加しました（補助用）。
  - [DEPLOY.md](DEPLOY.md): 本ドキュメントを追加・更新しました。

- **何を、どの順で実行したか**:
  1. リポジトリ内に直接書かれていた `service_key`（平文）を `.streamlit/secrets.toml` から削除しました。これにより誤ってコミットされるリスクを排除しました。
  2. `docker-compose.yml` を `.env` を参照する方式に書き換えました。これにより機密はローカルの `.env` か CI シークレットに安全に保管できます。
  3. systemd ユニットから直接キーを持つのをやめ、`EnvironmentFile` を使う方式に変更しました。サーバー側の `/etc/default/streamlit_<username>` にのみキーを置く運用を推奨します。
  4. `.gitignore` を追加して `.env` とシークレットファイルをコミットから除外するようにしました。
  5. Supabase のテーブル作成を自動化するためのスクリプトを作成し、サービスキーを用いて実行しましたが、対象プロジェクトでは PostgREST の `public.run_sql` 関数が有効化されておらず自動作成は失敗しました（PGRST202 エラー）。

- **手順（ユーザーが実行するコマンド）**:

  1) リポジトリルートに `.env` を作成（例）:

```bash
cat > .env <<EOF
SUPABASE_URL=https://hpzpkdyvjlvpfzbeddax.supabase.co
SUPABASE_KEY=sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data
EOF
```

  2) Docker で起動:

```bash
docker compose up -d --build
```

  3) systemd を使う場合（サーバー）:

```bash
# 例: /etc/default/streamlit_<username> を作成
sudo tee /etc/default/streamlit_<username> > /dev/null <<EOF
SUPABASE_URL=https://hpzpkdyvjlvpfzbeddax.supabase.co
SUPABASE_KEY=sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data
EOF

sudo cp deployment/streamlit.service /etc/systemd/system/streamlit@.service
sudo systemctl daemon-reload
sudo systemctl enable --now streamlit@<username>.service
sudo journalctl -u streamlit@<username>.service -f
```

  4) Supabase にテーブルがなければ、SQL エディタで以下を実行してください（最も確実）:

```sql
CREATE TABLE IF NOT EXISTS public.batting_data (
  id serial PRIMARY KEY,
  team_name text,
  player_name text,
  plate_id text,
  course text,
  pitch_type text,
  catch_position text,
  batted_ball_angle double precision,
  pitcher_hand text,
  count text,
  result text,
  input_datetime timestamp with time zone
);
```

- **補足とセキュリティ注意**:
  - 私がリポジトリ内のサービスキーを削除しましたが、既にコミット履歴に残っている場合は `git filter-branch` や `git filter-repo` 等で履歴から消す必要があります。
  - `.env` は運用上の秘匿データです。CI のシークレットやサーバーの `EnvironmentFile` を利用し、公開リポジトリには絶対に置かないでください。
  - 私が実行した `scripts/create_supabase_table.py` は管理RPCが有効であればテーブル作成を自動化しますが、多くの Supabase プロジェクトではこの RPC が無効化されているため、ダッシュボードでの手動実行が確実です。

## 次にあなたがやるべきこと

1. **Supabase のテーブルを作成する**
   - Supabase ダッシュボードにログインし、SQL エディタで以下を実行してください。

```sql
CREATE TABLE IF NOT EXISTS public.batting_data (
  id serial PRIMARY KEY,
  team_name text,
  player_name text,
  plate_id text,
  course text,
  pitch_type text,
  catch_position text,
  batted_ball_angle double precision,
  pitcher_hand text,
  count text,
  result text,
  input_datetime timestamp with time zone
);
```

2. **環境変数を安全に設定する**
   - プロジェクトルートに `.env` を作成し、次を追加します。

```bash
SUPABASE_URL=https://hpzpkdyvjlvpfzbeddax.supabase.co
SUPABASE_KEY=sb_publishable_Fr-2qh2FJ6h2eKoP6m55RA_sHLYKzRo
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_TABLE=batting_data
```

3. **Docker で起動する**
   - ローカル環境または Docker 対応サーバーで以下を実行します。

```bash
docker compose up -d --build
```

4. **起動後の確認**
   - `docker compose logs -f` でログを確認し、`Streamlit` が正常に起動したかを確かめます。
   - ブラウザで `http://localhost:8501` にアクセスし、アプリが表示されることを確認します。

5. **systemd を使う場合**
   - サーバーで `/etc/default/streamlit_<username>` を作成し、上と同じ環境変数を記載します。
   - `sudo systemctl daemon-reload` と `sudo systemctl enable --now streamlit@<username>.service` を実行します。

6. **動作確認後**
   - アプリが動作したら、`.env` をリポジトリにコミットしないことを再確認してください。
   - 必要なら、ログインページから `batting_data` への入力と保存が正常に働くかを実際にテストしてください。

- **代行を希望する場合**:
  - そのときは一時的な SSH 公開鍵、実行ユーザー、sudo 権限の有無を教えてください。鍵は短期間で無効化できるように設定してください。

---

