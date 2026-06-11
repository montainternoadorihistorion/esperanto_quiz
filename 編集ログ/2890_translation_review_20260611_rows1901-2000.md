# 2890語彙 日中韓注釈レビュー 1901-2000

作成日: 2026-06-11

対象範囲: 1901-2000（`ĉapelo` から `-id-` まで）

## 方針

- `{Ｂ}`、`>>...`、`=...`、`><...`、`[~...]` などの既存記法は維持。
- エスペラント語根の答えが通常注釈部分に不用意に露出していないかを確認。
- 正しい範囲内の表現差・多様性は残し、意味ズレや不要な外来語注釈だけを最小限修正。

## 修正した箇所

| 行 | 見出し語 | 言語 | 修正前 | 修正後 | 理由 |
|---:|---|---|---|---|---|
| 1959 | `ŝelo` | 中国語 | `外皮，壳；（海）船体；（空）机体；（计算机）命令解释器（shell）` | `外皮，壳；（海）船体；（空）机体；（计算机）命令解释器` | 中国語だけで意味が足りており、英語 `shell` はアプリ教材上の注釈として不要なため削除。保護記法 `=komandinterpretilo` は維持。 |

## 確認したが変更しなかった主な箇所

| 行 | 見出し語 | 確認内容 |
|---:|---|---|
| 1901 | `ĉapelo` | `=cirkumflekso` は関連語注記として維持。 |
| 1911 | `ĉemizo` | `>>tolaĵo` は参照注記として維持。 |
| 1913 | `ĉerizo` | `>>merizo` は参照注記として維持。 |
| 1923 | `ĉielo` | `>>firmamento` などの参照注記を維持。 |
| 1930 | `ĉokolado` | `>>〜` 記法を維持。 |
| 1933 | `ĝemelo` | `=dunaskito` は同義・関連語注記として維持。 |
| 1944 | `ĥoro` | `=koruso` は同義・関連語注記として維持。 |
| 1949 | `ĵurnalo` | `=taglibro` は関連語注記として維持。 |
| 1957 | `ŝati` | `=〜` 記法を維持。 |
| 1966 | `ŝlosi` | `[~ilo]` は派生語メモとして維持。 |
| 1969 | `ŝoforo` | `>>aŭtisto` は参照注記として維持。 |
| 1972 | `ŝpari` | `=〜gi` は派生語メモとして維持。 |
| 1977 | `ŝtato` | `>>〜` / `=〜` 記法を維持。 |
| 1981 | `ŝtopi` | `>>〜` 記法を維持。 |
| 1990-2000 | 接尾辞群 | `>>bros〜o`、`>>uz〜o`、`>>parti〜o`、`>>toki〜o` などの参照例は保護対象として維持。 |

## 反映ファイル

- `2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv`
- `編集ログ/2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv`
- `mobile_app/data/vocab.json`

## 検証結果

- `python3 tools/build_mobile_data.py` 済み（`vocab.json` 2890件、`sentences.json` 5000件）
- CSV行数・列数確認済み（2890行、9列）
- ルートCSVと編集ログコピーのバイト一致確認済み
- `ŝelo` の中国語注釈が `vocab.json` に反映されていることを確認済み
- 1901-2000範囲の通常注釈部分に、追加対応が必要な非保護ラテン文字列がないことを確認済み
- `python3 tools/validate_mobile_assets.py` 済み（Validation passed）
- `python3 -m unittest discover -s tests -p 'test_*.py'` 済み（69 tests OK）
