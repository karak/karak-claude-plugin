---
name: thoughtworks-radar-ref
description: |
  Thoughtworks Technology Radar (Vol.34, 2026-04 時点) の **構造インデックス + テーマ層** を
  参照するためのスキル。Blip (個別技術) の `name / ring / quadrant / radar_url / tags`
  と、ボリュームごとの **Themes (評価軸ナラティブ)** を分離保持する。
  本文 (説明文・テーマナラティブ) は Thoughtworks の著作権下にあるため配布物には含めず、
  **ユーザー端末ローカルのキャッシュに初回参照時 WebFetch して保存** する
  (キャッシュ場所は配布物の外: `~/.cache/karak-claude-plugin/thoughtworks-radar-ref/`)。

  MUST trigger when: Thoughtworks Technology Radar、Tech Radar、ThoughtWorks Radar、
  Adopt/Trial/Assess/Hold/Caution の判定、Vol.34、Codebase cognitive debt、
  Agent instruction bloat、MCP by default、Lethal Trifecta、
  Securing permission-hungry agents、Putting coding agents on a leash、
  Agentic security patterns、技術トレンドの一次情報照合、業界シグナル参照。

  Also triggers on:
  「Tech Radar で何と言っている?」「ThoughtWorks では Adopt?」「最新の Radar の AI 系」
  「Caution に入っているもの」「テーマで言うと」「業界として警戒されている」
  「採用判断の根拠として Radar を引きたい」「architecture-principles と Radar を突き合わせて」
  「coding agent のセキュリティで Radar は何を言っている?」。
---

# Thoughtworks Technology Radar Reference

## 著作権と配布方針 (最重要)

- Thoughtworks Technology Radar の **コンテンツ (Blip 説明文、Themes ナラティブ)** は
  「© Thoughtworks, Inc.」 で保護される。公開 CC ライセンス等は宣言されていない (2026-05 確認時点)。
- 本スキルの **配布物 (この git リポジトリ)** には **構造インデックスのみ** を含める:
  `name / ring / quadrant / volume / radar_url / tags` といった事実情報および
  Theme の `id / title / source_url / related_blip_names`。これらは創作的表現ではなく
  事実分類なので著作権の対象外と判断する。
- **説明文・テーマナラティブ本文は、ユーザー端末上のキャッシュ** に
  初回参照時 `WebFetch` で取得・保存する。キャッシュはスキル配布物の外:

  ```
  ${XDG_CACHE_HOME:-$HOME/.cache}/karak-claude-plugin/thoughtworks-radar-ref/v<NN>/
  ```

  これは「ユーザー自身が Thoughtworks のサイトを読みに行く」のと同じ法的位置づけ
  (ブラウザキャッシュと同様) で、再配布にはあたらない。
- 出典: <https://www.thoughtworks.com/radar> (Vol.34, 2026-04)
- ユーザに提示する際は **要約と出典 URL** を返す。長文の逐語引用は避ける。

このルールは設計上の不可侵制約。スナップショットを「リッチに見せる」ために
TW の説明文を `blips.json` / `themes.json` 本体にコピーしてはならない。

---

## 核心原則

1. **二層モデルで照会する**
   - **Blip 層**: 個別技術 (`references/blips.json`) — *What* に答える
   - **Theme 層**: 評価軸ナラティブ (`references/themes.json`) — *Why / How* に答える
   - フラットな Blip リストだけでは「マクロな解釈」が抜ける。Caution 系の問いには必ず Theme を併読する。

2. **配布物はインデックス、本文はキャッシュ経由**
   - 説明文が必要な場合、まずキャッシュ (`<cache_dir>/blip_summaries.json` 等) を見る。
   - キャッシュにヒットしなければ `radar_url` を `WebFetch` し、結果をキャッシュに書き込む。
   - キャッシュは **ボリュームごとに分離** (`v34/`, `v35/` ...)。新ボリュームが出たら自然に再フェッチされる。

3. **ring の語彙は Vol.34 準拠 (`Caution` を採用)**
   - Vol.34 で **Hold → Caution** に改名。意味も "Do not use" (passive) から
     "Proceed with care" (evaluative) へシフト。
   - 古い `Hold` 表記が混在する文献を扱う際は `Caution` と意味的に同義として扱う。

4. **Theme と Blip は多対多**
   - 1 つの Theme は複数 Blip を束ねる。1 つの Blip は複数 Theme から参照される。
   - `themes.json` の `related_blip_names` は **本スキル作者の解釈** に基づくマッピング。
     Thoughtworks の原文ではない点を明示する。

---

## ファイル構成

```
thoughtworks-radar-ref/
├── SKILL.md                    (このファイル)
├── references/
│   ├── source_info.json        クロスボリューム不変項 + latest_volume ポインタ
│   ├── radar-schema.json       record shape / enum の JSON Schema ($schema_version あり)
│   └── volumes/
│       ├── v34/
│       │   ├── manifest.json   v34 固有のメタ (date, ring_vocabulary, ring_changes_from_prev, ...)
│       │   ├── blips.json      v34 Blip インデックス (name / ring / quadrant / volume / radar_url / tags / note?)
│       │   └── themes.json     v34 Themes インデックス (id / title / volume / source_url / related_blip_names / our_synthesis?)
│       └── v<NN>/              将来ボリューム — v34 を編集せず追加できる
└── scripts/
    ├── cache_helpers.py        キャッシュ I/O ユーティリティ (stdlib のみ)
    └── refresh_cache.py        全 Blip/Theme の WebFetch 結果を一括キャッシュするヘルパー
```

**設計上の関心分離**:
- `source_info.json` — クロスボリューム不変 (TW のベース URL、キャッシュ規約、著作権ステートメント、`latest_volume` ポインタ)。ボリューム更新時に編集するのは `latest_volume` のみ。
- `volumes/v<NN>/manifest.json` — そのボリューム固有の事実 (`date`, `ring_vocabulary`, `quadrant_urls`, `ring_changes_from_prev`, snapshot 取得日)。ボリュームを跨いでドリフトする値はここに閉じ込める。
- `radar-schema.json` — record shape と enum。Caution が追加されたように語彙が拡張されたら `$schema_version` を bump。普段は触らない。
- `volumes/v<NN>/{blips,themes}.json` — そのボリュームの構造インデックス本体。

**キャッシュ側 (配布物に含まれない)**:

```
${XDG_CACHE_HOME:-$HOME/.cache}/karak-claude-plugin/thoughtworks-radar-ref/v34/
├── blip_summaries.json         { "<blip_name>": { "summary": "...", "fetched_at": "..." } }
├── theme_narratives.json       { "<theme_id>":  { "narrative": "...", "fetched_at": "..." } }
└── .meta.json                  { volume: 34, last_full_refresh: "..." }
```

---

## 照会フロー (Routing)

### 段階 0 — ボリューム解決

```
references/source_info.json を読み latest_volume を取得 (例: 34)
→ 以降の参照は references/volumes/v34/{blips,themes,manifest}.json
```

ユーザーが特定ボリュームを指定したら (例: 「Vol.33 では」) `v33/` を見る。
無ければ「該当ボリュームのスナップショットは未収録」と明示し、WebFetch にフォールバック。

### 段階 1 — インデックス照合 (常にローカルで完結)

```
問い → volumes/v<NN>/{blips,themes}.json を読む → 該当 Blip/Theme の name と radar_url を抽出
```

| 問いの形 | 開くファイル | 操作 |
|---|---|---|
| 「X は Radar で何環?」 | `volumes/v<NN>/blips.json` | name 一致 → `ring` を返す |
| 「Caution に入っているものは?」 | `volumes/v<NN>/blips.json` | `select(.ring == "Caution")` |
| 「`tag: security` の Caution は?」 | `volumes/v<NN>/blips.json` | `select(.ring == "Caution" and (.tags // []) | index("security"))` |
| 「Theme X に関連する Blip は?」 | `volumes/v<NN>/themes.json` | `select(.id == "X") | .related_blip_names` |
| 「このボリュームの ring 語彙は?」 | `volumes/v<NN>/manifest.json` | `.ring_vocabulary` |
| 「Vol.X と Vol.X-1 で何が変わった?」 | `volumes/v<NN>/manifest.json` + 旧 v<NN-1>/ | `ring_changes_from_prev` を起点に diff |

ここで止まれる問いは、配布物だけで答えが完結する。

### 段階 2 — キャッシュ照会 (説明文が必要なとき)

```
キャッシュパス = ~/.cache/karak-claude-plugin/thoughtworks-radar-ref/v<volume>/
1. blip_summaries.json を読む
2. キーに blip name があればそれを返す
3. 無ければ radar_url を WebFetch → 結果を blip_summaries.json に追記 → 返す
```

擬似コード (`scripts/cache_helpers.py` を呼び出すパターン):

```python
from cache_helpers import get_or_fetch_summary

# fetcher は radar_url を受け取り要約テキストを返す関数。
# Claude Code セッション内では WebFetch ツールへの薄いラッパが該当する。
text = get_or_fetch_summary(
    blip_name="Codebase cognitive debt",
    fetcher=lambda url: webfetch(url, "Return the official summary paragraph."),
    volume=34,
)
```

`fetcher=None` で呼ぶと純粋なキャッシュ読みになる (`get_cached_summary` と等価)。
細かい制御が要るときは `get_cached_summary` / `write_cached_summary` を直接使う。

Claude Code セッションから直接行う場合:

```
1. ~/.cache/karak-claude-plugin/thoughtworks-radar-ref/v34/blip_summaries.json を Read
2. キーがあれば値を使う
3. 無ければ WebFetch(radar_url, "Extract the official summary text") → JSON を Edit/Write
```

### 段階 3 — 一次情報直接参照 (スナップショット範囲外)

- 「Vol.34 以降の新 Blip は?」 → `source_info.json` の `main_url` を WebFetch
- 「最新の Themes は?」 → 同じく WebFetch (Themes は `/radar` トップに inline)

---

## `jq` 例

```bash
# 最新ボリュームを動的に解決
V=$(jq -r '.latest_volume' references/source_info.json)
BLIPS=references/volumes/v${V}/blips.json
THEMES=references/volumes/v${V}/themes.json

# Caution + security タグ
jq '[.[] | select(.ring == "Caution") | select((.tags // []) | index("security"))]' "$BLIPS"

# 特定テーマに関連する Blip 一覧
jq '.[] | select(.id == "securing-permission-hungry-agents") | .related_blip_names' "$THEMES"

# このボリュームの ring 語彙
jq '.ring_vocabulary' references/volumes/v${V}/manifest.json

# キャッシュにある Blip 名一覧
jq 'keys' "${XDG_CACHE_HOME:-$HOME/.cache}/karak-claude-plugin/thoughtworks-radar-ref/v${V}/blip_summaries.json"
```

---

## アンチパターン

- **`blips.json` の `note` 欄に TW の説明文をペーストする**: 著作権上、配布物に TW の原文を入れない。
  `note` は本スキル作者の解釈・社内補足のみ。
- **Theme ナラティブを `themes.json` 本体にコピーする**: 同上。`our_synthesis` は karak 視点の
  **要約方針メモ** であり、TW 原文の引用ではない。
- **`Caution` を「Hold」と読み替えて回答する**: Vol.34 のセマンティクス変更を見落とすことになる。
- **Theme を見ずに「Caution = 使うな」と断ずる**: Caution の意図はテーマナラティブで初めて成立する。
- **スナップショットを「最新」と称する**: `source_info.json` の `volume` / `date` を必ず添えて、相対化する。
- **キャッシュをスキルディレクトリ内に作る**: 著作権上、TW のテキストが git に入る経路になる。
  必ず `~/.cache/...` 配下に置く。

---

## 更新フロー

### 新ボリューム (Vol.X+1) 公開時

1. **新しいボリュームディレクトリを作る**: `references/volumes/v<X+1>/` を mkdir。**旧 `v<X>/` は触らない** — 履歴として保持。
2. **`v<X+1>/blips.json` を生成**:
   - 4 quadrant ページ (`/radar/techniques`, `/radar/platforms`, `/radar/tools`,
     `/radar/languages-and-frameworks`) を WebFetch → 各 Blip の
     `name / ring / quadrant / radar_url` を構造抽出して `blips.json` を組み立てる。
     注: `refresh_cache.py` はあくまでユーザー端末キャッシュを埋めるツールであり、
     配布物の `blips.json` を生成する責務は持たない (Index は人間の編集対象)。
3. **`v<X+1>/themes.json` を手書き**: 新ボリュームの Themes を `/radar` ページから把握し、
   `id / title / source_url / related_blip_names` のみ記録 (ナラティブは入れない)
4. **`v<X+1>/manifest.json` を作る**: `date`, `ring_vocabulary`, `quadrant_urls`,
   `ring_changes_from_prev` (前ボリュームから何が変わったか), `snapshot_fetched_at` を記入
5. **`source_info.json` の `latest_volume` を `X+1` に bump**。他は触らない (URL や規約が変わっていなければ)
6. **schema 変更が必要なら** (新 ring が追加された等): `radar-schema.json` の enum を拡張し
   `$schema_version` を bump。CHANGELOG 相当のメモを manifest の `notes` に残す
7. **キャッシュ側 (端末ローカル)**: 新ディレクトリ `<cache>/v<X+1>/` が自動的に使われる。旧キャッシュは残してよい
8. **コミット時の自己点検**:
   - [ ] TW 原文の長文引用が配布物に混入していないか — `radar_url` / `source_url` 以外の文字列フィールドが長すぎないかをスキャン:
         `jq '[.[] | {name: (.name // .id), note_len: ((.note // .our_synthesis // "") | length)}] | map(select(.note_len > 400))' references/volumes/v*/blips.json references/volumes/v*/themes.json`
         (400 字超は karak 解釈メモとしても疑わしい — TW 本文を貼り付けていないか確認)
   - [ ] `ring` が `manifest.json` の `ring_vocabulary` と整合しているか
   - [ ] `related_blip_names` が同ボリュームの `blips.json` の `name` と綴り一致しているか
   - [ ] `cache/` のような名前のディレクトリが配布物に混入していないか
   - [ ] 旧 v<X>/ を誤って編集していないか (履歴破壊防止)

### 個別 Blip の説明文を読みたいとき (利用時)

`scripts/cache_helpers.py` の `get_or_fetch_summary()` を使う。
キャッシュにヒットすれば即時、なければ `radar_url` を WebFetch してキャッシュに書く。

---

## architecture-principles との関係

このスキルは [[architecture-principles]] の **業界シグナル重みづけ** のうち
"Tech Radar" シグナルを具体化するレイヤー。`architecture-principles` 側が概念を選び、
本スキルが「最新の Radar における重み (Adopt/Trial/Assess/Caution)」と
「マクロ評価軸 (Themes)」を返す関係。

両者を併用するときの推奨手順:

1. `architecture-principles` で 5 層モデル診断 → 候補概念抽出
2. 候補概念のうち Radar に登場する Blip を `blips.json` で照合
3. `themes.json` で「なぜそう判定されたか」のマクロ文脈を確認
4. 必要な箇所だけキャッシュ/WebFetch で TW の一次記述を取りに行く
5. ADR には「Radar Vol.X による位置づけ」を一次情報として記載
