# 2890 CSV 日中韓注釈レビュー rows 0801-0900（2026-06-11）

対象: `2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv`

依頼文で指定されている `251129_plajnova copy.csv` そのものは現行作業ツリーには見当たらないため、現在アプリで使われている最新版候補の `260505_plej_nova.csv` を点検対象とした。

## 点検範囲

- CSVデータ行: 801-900
- 対象語根: `kombi` から `krokodilo` まで
- 対象列: `Japanese_Trans`, `Chinese_Trans`, `Korean_Trans`

## CSV本文に反映した修正

| 行 | 語根 | 列 | 旧 | 新 | 理由 |
|---:|---|---|---|---|---|
| 897 | `kristalo` | Japanese_Trans | `{Ｂ}【化】結晶; クリスタルガラス（鉱物の水晶は kvarco）` | `{Ｂ}【化】結晶; クリスタルガラス（鉱物の水晶は石英を指す）` | `kvarco` が通常文中に直接出ていたため、同じ補足内容を日本語化して、注釈内でエスペラント語根を露出させない原則に合わせた。 |

同じ修正を `編集ログ/2890 Gravaj Esperantaj Vortoj kun Signifoj en la Japana, Ĉina kaj Korea_260505_plej_nova.csv` にも反映し、ルートCSVとの一致を維持した。

## 個別に見たが修正しない項目

| 行 | 語根 | 判断 |
|---:|---|---|
| 803 | `komedio` | `><〜` と `>>farso` は参照記法として維持。喜劇と茶番の転義は三言語で対応。 |
| 812 | `kompanio` | 会社・仲間/一行・軍の中隊の幅が日中韓で対応。 |
| 818 | `komponi` | 構成・創作・作曲・化学的構成の範囲が三言語で保たれている。 |
| 827 | `konduki` | 導く・連れて行く・通じる・指揮する・運転するの幅があり、`=stiri`, `=〜ti` は参照記法として維持。 |
| 833 | `konfirmi` | 確認・立証・承認の範囲が保たれている。`=〜acii` は参照記法として維持。 |
| 842 | `konscii` | 自覚・意識するの説明として妥当。補語の取り方に関する日本語注記も有用。 |
| 850 | `konstanta` | 不変・一定・絶え間ない・志操堅固の幅が三言語で対応。 |
| 855 | `kontanta` | 即時払い・現金の意味が明確。`>>kredita` は参照記法として維持。 |
| 864 | `kordo` | 音楽の弦・心の琴線・解剖・数学の弦が三言語で対応。 |
| 872 | `korvo` | `>>korako`, `>>〜`, `>>monedo` は参照記法として維持。カラス属/カラス科の説明として妥当。 |
| 873 | `kosmo` | 宇宙と秩序ある体系の転義があり、`><kaoso` は反対語参照として維持。 |
| 876 | `koto` | `>>ŝlimo` は参照記法として維持。泥と汚辱の転義は三言語で対応。 |
| 887 | `kredito` | 信用・掛け・簿記の貸方の範囲があり、`><〜` は参照記法として維持。 |
| 897 | `kristalo` | 修正後も「化学の結晶」と「クリスタルガラス」の範囲は維持。鉱物の水晶補足は日本語化した。 |
| 900 | `krokodilo` | 中国語の `[~i]` は派生語メモ記法として維持。日中韓ともワニの基本義は明確。 |

## 実施した機械確認

- rows 0801-0900 について、日中韓注釈に保護されていないラテン文字列が残っていないかを簡易チェック。
- 修正後、同範囲で未保護のラテン文字列は0件。
- PIV2020ローカルデータで、判断に迷いやすい `komitat/o`, `komun/a`, `kondiĉ/o`, `konduk/i`, `konfes/i`, `konsci/i`, `konsent/i`, `konsider/i`, `konstant/a`, `konstru/i`, `kor/o`, `kost/i`, `kre/i`, `kred/i`, `kresk/i`, `lingv/o` の見出し存在を確認。
- `mobile_app/data/vocab.json` を再生成し、`kristalo` の日本語注釈が反映済みであることを確認。

## 変更

- CSV本文: 1セル修正
- mobile data: `mobile_app/data/vocab.json` を再生成
- 音声: 変更なし
