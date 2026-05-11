# Streamlit Cloud デプロイ手順（Google Sheets 連携）

本番用シークレットを誤ってコミットしないための作業手順をまとめます。

## スマホ向けUIについて

スマートフォンでの利用は `mobile_app/` の `localStorage` 保存型UIを優先します。`app.py` と `sentence_app.py` はスマホアクセスを検出すると、このUIをStreamlitコンポーネントとして表示します。PCユーザーは従来のStreamlit版をそのまま使えます。

- エントリポイント: `mobile_app/index.html`
- Streamlit連携: `mobile_streamlit_bridge.py`
- サービスワーカー: `mobile-sw.js`
- PWA用データ: `mobile_app/data/vocab.json`, `mobile_app/data/sentences.json`
- スマホ状態保存: ブラウザの `localStorage`
- 進行中クイズの保護: 再開導線を表示し、新規開始で上書きする前に確認
- 音声: 静的PWA単独起動では利用可。Streamlit Cloud内蔵表示では音声ファイルの直接配信を避けるためオフ。

Streamlitの静的ファイル配信はHTML/JSアプリ配信向けではないため、Streamlit Cloudではカスタムコンポーネントとして埋め込みます。CSV更新後は次を実行してJSONを更新します。

```bash
python3 tools/build_mobile_data.py
```

PCでスマホUIを強制表示する確認URL:

```text
https://<your-app>.streamlit.app/?mobile_app=1
```

スマホで従来版を確認するURL:

```text
https://<your-app>.streamlit.app/?classic=1
```

## 1. シークレットの準備（ローカルで開かない）
- `gen-lang-client-0360673218-9b47aa22b42f.json` は **コミットしない**（`.gitignore` 済み）。
- JSON を開く必要がある場合はローカルで確認し、`private_key` の改行を `\n` に置換しておく。

## 2. Streamlit Cloud の Secrets 設定
1. Streamlit Cloud のデプロイページで **Secrets** を開く。
2. 以下を貼り付け、`project_id`・`client_email`・`private_key` を JSON から転記する（改行は `\n`）。
   ```toml
   [connections.gsheets]
   type = "service_account"
   project_id = "gen-lang-client-0360673218"
   private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
   client_email = "streamlit-sheets-sa@gen-lang-client-0360673218.iam.gserviceaccount.com"
   spreadsheet = "https://docs.google.com/spreadsheets/d/1WnlZ2BACdf3uCha0JOscdk2wPselC_VVm_Ua6VlhC-I"
   ```
3. 保存後にアプリを再デプロイする。

## 3. 動作確認（手順）
1. デプロイされたアプリをスマホで開き、スマホUIが表示されることを確認。
2. 任意のユーザー名でクイズを開始し、数問回答する。
3. ブラウザを再読み込みし、進行中のクイズが復元されることを確認。
4. 不正解を出した場合、復習対象が保持されることを確認。
5. 設定画面へ戻った場合に「続きから再開」が表示され、新規開始時に上書き確認が出ることを確認。
6. 結果画面と成績画面がスマホ幅で読みやすいことを確認。
7. 従来版を確認する場合は `?classic=1` を付けて開く。

## 4. ローカルの鍵ファイルの扱い
- 作業後は鍵ファイルを安全な場所に移動するか削除する。
- 追加で鍵を扱う場合は、`.gitignore` にあることを確認し、誤ってステージングしないよう注意する。

## 5. 依存関係
- `requirements.txt` に `streamlit`, `pandas`, `streamlit-gsheets` を記載済み。Cloud で自動インストールされる。

## 6. トラブルシュートのヒント
- 認証エラー: Secrets の `private_key` の改行が `\n` に置換されているか確認。
- 書き込みエラー: Sheets 側でサービスアカウントが「編集者」権限になっているか確認。
- 反映遅延: ネットワーク遅延の場合があるため数秒待つ。キャッシュは `ttl=0` なので基本即時反映。
