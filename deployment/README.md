常時起動手順

このフォルダには Streamlit アプリを常時起動するためのスクリプトと systemd ユニット定義があります。

推奨手順（Linux マシン・systemd が利用可能）:

1. 依存をインストール

```bash
cd /workspaces/baseball-analysis-of-batter
python -m pip install -r requirements.txt
```

2. systemd ユニットをコピーしてユーザー名を設定（%i に置き換え不要、systemd のテンプレートを利用します）

```bash
sudo cp deployment/streamlit.service /etc/systemd/system/streamlit@youruser.service
sudo systemctl daemon-reload
sudo systemctl enable --now streamlit@youruser.service
```

実際には `/etc/systemd/system/streamlit@youruser.service` の `User=` を `youruser` に置き換えてください。

3. ログ確認

```bash
journalctl -u streamlit@youruser.service -f
# または
tail -n 200 logs/streamlit.log
```

軽量な代替（systemd が使えない場合）:

```bash
cd /workspaces/baseball-analysis-of-batter
nohup bash deployment/start_streamlit.sh &
```

コンテナ運用や外部サーバでの運用に切り替える場合は `Dockerfile` と `docker-compose.yml` を用意し、`restart: always` を設定することを推奨します。
