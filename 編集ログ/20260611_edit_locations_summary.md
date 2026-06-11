# 2026-06-11 編集箇所まとめ

作成日: 2026-06-11

この文書は、直近の一連の作業で「結局どこを編集したのか」を後から確認しやすくするための入口である。
細かい全セルの旧値・新値は既存の個別ログに残し、この文書では編集対象ファイル、編集範囲、件数、代表的な変更箇所を整理する。

## 最短結論

実データとして編集した中心ファイルは次の2系統。

| 系統 | 実際に編集した主ファイル | 内容 |
|---|---|---|
| 例文5000行 | `phrases_eo_en_ja_zh_ko_ru_fulfilled_260505.csv` | エスペラント本文の自然化・日中韓訳の整合修正 |
| 語彙2890語 | `2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv` | 日中韓注釈の小修正 |

アプリ用の派生データとして、次も再生成・更新した。

| 派生ファイル | 目的 |
|---|---|
| `mobile_app/data/sentences.json` | 例文CSVの変更をスマホ版データへ反映 |
| `mobile_app/data/vocab.json` | 語彙CSVの変更をスマホ版データへ反映 |
| `mobile_app/data/audio_manifest.json` | Google Drive音声リンクの整合状態を反映 |

## 1. 例文CSVのエスペラント本文修正

対象ファイル:

- `phrases_eo_en_ja_zh_ko_ru_fulfilled_260505.csv`
- 派生データ: `mobile_app/data/sentences.json`
- 音声関連: `mobile_app/data/audio_manifest.json`

内容:

- `minibaro` のような強引な外来語化、英語・ロシア語の直訳調、文法・語法上かなり不安定な表現を点検。
- 明確に直した方がよい箇所だけを修正。
- エスペラント本文変更は最終的に125行。
- 訳だけの焦点調整は2行。
- 修正文の音声は RHVoice `spomenka` で作成済み。
- Google Drive側は最終確認で matched 5000 / missing 0 / extra 0。

詳細ログ:

- `編集ログ/phrases_eo_forced_loanwords_findings_20260610.md`
- `編集ログ/phrases_eo_forced_loanwords_corrections_summary_20260610.md`
- `編集ログ/drive_audio_extra_files_to_delete_20260611.md`

代表的な修正例:

| PID | 修正前 | 修正後 | 理由 |
|---:|---|---|---|
| 2271 | `Kie estas la parkometro?` | `Kie estas la pagmaŝino por parkumado?` | 駐車料金精算機の意味を明確化 |
| 2704 | `Rezervoj estis faritaj por mi kaj mia familio` | `Ĉambroj estas rezervitaj por mi kaj mia familio` | ホテル文脈の予約対象を明示 |
| 2918 | `Ĉu vi povus fari rezervon por mi?` | `Ĉu vi povus rezervi tablon por mi?` | レストラン文脈の予約対象を明示 |
| 3248 | `Li havos grilitan karpon` | `Li prenos kradrostitan karpon` | 飲食の `havi` と `grilita` を自然化 |
| 3999 | `Kiom kostas lui malsekkostumon por unu tago?` | `Kiom kostas lui plonĝkostumon por unu tago?` | `wetsuit` 直訳を避ける |
| 4934 | `Ĉu vi havas fotokabinon?` | `Ĉu vi havas fotobudon?` | 不安定な外来語化を避ける |

保持した方針:

- `regato`, `smuzio`, `toasto`, `Mi feriumas`, `Mi faras praktikon` など、正しい範囲内の多様な表現は維持。
- エスペラント学習教材として、過度な純化は避けた。

## 2. 例文CSVの日中韓訳修正

対象ファイル:

- `phrases_eo_en_ja_zh_ko_ru_fulfilled_260505.csv`
- 派生データ: `mobile_app/data/sentences.json`

内容:

- JA/ZH/KO列のみを修正。
- EO列とEN列は変更していない。
- したがって、この日中韓訳修正自体は音声再生成を伴わない。
- 第1から第4ラウンド合計で395セルを改善。

詳細ログ:

- `編集ログ/cjk_translation_fixes_20260611_round1.md`
- `編集ログ/cjk_translation_fixes_20260611_round2.md`
- `編集ログ/cjk_translation_fixes_20260611_round3.md`
- `編集ログ/cjk_translation_fixes_20260611_round4.md`

ラウンド別の編集内容:

| ラウンド | 件数 | 主な編集内容 |
|---|---:|---|
| R1 | 77セル | EO変更行に合わせた日中韓訳の意味整合、句読点の規約統一 |
| R2 | 263セル | 全5000行の日中韓品質監査。意味ズレ、専門用語、文体、地域語、韓国語数詞など |
| R3 | 43セル | 異なるEO文が同じ訳になっていた逆方向クイズ衝突を解消 |
| R4 | 12セル | 同一EO文が異なる訳になっていた順方向クイズ衝突を調和 |

R4で編集した5クラスタ:

| 対象PID | EO | 調和先 | 変更セル |
|---|---|---|---|
| 165 / 176 | `Ĝis revido!` | さようなら！ / 再见！ / 안녕히 가세요! | 176の3言語 |
| 223 / 227 | `Nedankinde` | 不客气。 / 천만에요. | 227の中韓 |
| 307 / 311 | `Atendu momenton` | 잠시만요. | 311の韓 |
| 323 / 343 | `Bone` | 承知しました。 / 好的。 / 알겠습니다. | 343の3言語 |
| 1908 / 1923 | `Ĉu estas iuj ekskursoj?` | ツアーはありますか？ / 有导览团吗？ / 투어가 있나요? | 1923の3言語 |

## 3. 語彙2890語CSVの日中韓注釈修正

対象ファイル:

- `2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv`
- 同期コピー: `編集ログ/2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv`
- 派生データ: `mobile_app/data/vocab.json`

補足:

- 依頼文に出ていた `251129_plajnova copy.csv` は現行作業ツリーに見当たらなかったため、現在アプリで使われている `260505_plej_nova.csv` を対象にした。
- CSV本文として最終的に変更を残したセルは6件。
- いったん変更したが、依頼文の「語根露出・未解決参照・派生語メモ記法は現状維持。過去に修正していれば元に戻す」という条件に合わせて復元したセルは4件。
- それ以外の範囲は、100行ごとのレビュー記録を残したが、本文は変更していない。
- 語彙CSV修正では音声ファイルは変更していない。

最終的に変更を残した6セル:

| 行 | 語根 | 言語 | 修正前 | 修正後 | 理由 |
|---:|---|---|---|---|---|
| 924 | `kupono` | 中国語 | `券，票券（coupon）；票券存根；（经）息票` | `券，票券；票券存根；（经）息票` | 不要な英語補足を削除 |
| 1520 | `romano` | 中国語 | `长篇小说，传奇小说（romance）；（史）骑士传奇；（史）罗马人，罗马市民` | `长篇小说，传奇小说；（史）骑士传奇；（史）罗马人，罗马市民` | 不要な英語補足を削除 |
| 1959 | `ŝelo` | 中国語 | `外皮，壳；（海）船体；（空）机体；（计算机）命令解释器（shell）` | `外皮，壳；（海）船体；（空）机体；（计算机）命令解释器` | 不要な英語補足を削除 |
| 2303 | `referenco` | 中国語 | `参照，参考，对照；推荐证明；（信息）引用（reference）、指针；参照基准` | `参照，参考，对照；推荐证明；（信息）引用、指针；参照基准` | 不要な英語補足を削除 |
| 2372 | `uzino` | 中国語 | `（大型）工厂；工业装置（plant）` | `（大型）工厂；工业装置` | 不要な英語補足を削除 |
| 2887 | `ŝakalo` | 韓国語 | `재칼` | `자칼` | ジャッカルの韓国語表記を自然化 |

再監査で復元した4セル:

| 行 | 語根 | 言語 | 復元前 | 復元後 | 理由 |
|---:|---|---|---|---|---|
| 193 | `bendo` | 日本語 | `{Ｂ}ひも, テープ, 帯, バンド; 【建】帯飾り（車のタイヤは通常〜とは呼ばない）` | `{Ｂ}ひも, テープ, 帯, バンド; 【建】帯飾り（車のタイヤは通常 pneŭo）` | 語根露出を含む既存注記として復元 |
| 425 | `fadeno` | 日本語 | `{Ｂ}糸, 線; 筋, 脈絡（針金は通常、別語（金属線）を用いる）` | `{Ｂ}糸, 線; 筋, 脈絡（針金は通常、別語（metal〜）を用いる）` | 語根露出を含む既存注記として復元 |
| 897 | `kristalo` | 日本語 | `{Ｂ}【化】結晶; クリスタルガラス（鉱物の水晶は石英を指す）` | `{Ｂ}【化】結晶; クリスタルガラス（鉱物の水晶は kvarco）` | 語根露出を含む既存注記として復元 |
| 1005 | `loĝi` | 日本語 | `{Ｂ}［自］住む, 居住する; 《広》滞在する（短期の宿泊はふつう宿泊系の別語を用いる）` | `{Ｂ}［自］住む, 居住する; 《広》滞在する（短期の宿泊はふつう gastejo/gasti）` | 語根露出を含む既存注記として復元 |

100行ごとのレビュー記録:

- `編集ログ/2890_translation_review_20260611_rows0001-0100.md`
- `編集ログ/2890_translation_review_20260611_rows0101-0200.md`
- `編集ログ/2890_translation_review_20260611_rows0201-0300.md`
- `編集ログ/2890_translation_review_20260611_rows0301-0400.md`
- `編集ログ/2890_translation_review_20260611_rows0401-0500.md`
- `編集ログ/2890_translation_review_20260611_rows0501-0600.md`
- `編集ログ/2890_translation_review_20260611_rows0601-0700.md`
- `編集ログ/2890_translation_review_20260611_rows0701-0800.md`
- `編集ログ/2890_translation_review_20260611_rows0801-0900.md`
- `編集ログ/2890_translation_review_20260611_rows0901-1000.md`
- `編集ログ/2890_translation_review_20260611_rows1001-1100.md`
- `編集ログ/2890_translation_review_20260611_rows1101-1200.md`
- `編集ログ/2890_translation_review_20260611_rows1201-1300.md`
- `編集ログ/2890_translation_review_20260611_rows1301-1400.md`
- `編集ログ/2890_translation_review_20260611_rows1401-1500.md`
- `編集ログ/2890_translation_review_20260611_rows1501-1600.md`
- `編集ログ/2890_translation_review_20260611_rows1601-1700.md`
- `編集ログ/2890_translation_review_20260611_rows1701-1800.md`
- `編集ログ/2890_translation_review_20260611_rows1801-1900.md`
- `編集ログ/2890_translation_review_20260611_rows1901-2000.md`
- `編集ログ/2890_translation_review_20260611_rows2001-2100.md`
- `編集ログ/2890_translation_review_20260611_rows2101-2200.md`
- `編集ログ/2890_translation_review_20260611_rows2201-2300.md`
- `編集ログ/2890_translation_review_20260611_rows2301-2400.md`
- `編集ログ/2890_translation_review_20260611_rows2401-2500.md`
- `編集ログ/2890_translation_review_20260611_rows2501-2600.md`
- `編集ログ/2890_translation_review_20260611_rows2601-2700.md`
- `編集ログ/2890_translation_review_20260611_rows2701-2800.md`
- `編集ログ/2890_translation_review_20260611_rows2801-2890.md`

## 4. 変更したが本文データではないもの

| ファイル | 内容 |
|---|---|
| `.gitignore` | ローカル生成物などを追跡対象から外すための小修正 |
| `編集ログ/*.md` | 作業判断、修正一覧、Drive確認結果、レビュー記録 |
| `tools/build_drive_audio_manifest.py` | Drive音声manifest作成のための補助スクリプト更新 |

## 5. 変更していないもの

| 対象 | 状態 |
|---|---|
| 例文CSVの日中韓R1-R4でのEO列 | 変更なし |
| 例文CSVの日中韓R1-R4でのEN列 | 変更なし |
| 語彙2890語レビューでの音声 | 変更なし |
| Google Sheets等への途中状態保存 | 実装していない |
| Google Drive上の手作業削除 | ユーザー側で実施。こちらではmanifest確認のみ |

## 6. 検証結果

確認済みの主な結果:

- `python3 tools/build_mobile_data.py`: 成功
- `mobile_app/data/sentences.json`: 5000件
- `mobile_app/data/vocab.json`: 2890件
- `python3 tools/validate_mobile_assets.py`: Validation passed
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 69 tests OK
- Drive音声: matched 5000 / missing 0 / extra 0
- 語彙CSV本体と編集ログ内同期コピー: 一致確認済み

## 7. 関連コミット

| commit | 内容 |
|---|---|
| `01e5a11` | エスペラント例文本文修正とDrive manifest整合 |
| `dc9f259` | 日中韓訳R1/R2とDrive manifest整合 |
| `33bd7b4` | 日中韓訳R3/R4のクイズ衝突解消 |
| `a662a90` | 語彙2890語レビューの最終反映 |

この文書自身は、上記の変更内容を後から追うための追加説明文書である。
