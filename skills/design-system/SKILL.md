---
name: design-system
description: >
  ウェブサイトやアプリのデザインシステムを作成・適用するスキル。55の実在するプロダクトのデザインシステム（色、タイポグラフィ、コンポーネント、レイアウト）をリファレンスとして保持し、
  ユーザーの要望に最適なデザインを提案・実装する。
  以下のキーワードでトリガーされる：
  - 「〇〇のようなデザインで」「〇〇風のデザイン」「〇〇みたいなサイト」（サイト名ベース）
  - 「モダンなデザイン」「ダークモードのサイト」「ミニマルなUI」「温かみのあるデザイン」（雰囲気ベース）
  - 「緑系のサイト」「青と白のデザイン」「グラデーションを使ったサイト」（色使いベース）
  - 「design system」「デザインシステム」「カラーパレット」「タイポグラフィ」
  - サイト名直接指定: Stripe, Linear, Vercel, Notion, Airbnb, Apple, Spotify, Figma, Framer,
    Supabase, Claude, Cursor, Raycast, Coinbase, Uber, Resend, Cal, PostHog, Wise, SpaceX,
    Revolut, Pinterest, Webflow, Miro, Intercom, BMW, NVIDIA, Warp, ElevenLabs, Superhuman,
    Mistral, Airtable, Clay, Sentry, Zapier, MongoDB, HashiCorp, Kraken, Expo, Mintlify,
    Sanity, Lovable, ClickHouse, Composio, Cohere, Minimax, Ollama, OpenCode, Replicate,
    RunwayML, Together AI, VoltAgent, xAI, IBM
---

# Design System Skill

55の実在するプロダクトのデザインシステムをリファレンスとして、ウェブサイトやアプリのUI/デザインシステムを作成・適用する。

## When to Use

- 「Stripeのようなデザインで」などサイト名を指定されたとき
- 「ダークモードのかっこいいサイト」など雰囲気・トーンで指定されたとき
- 「緑と黒のカラーリング」など色使いで指定されたとき
- デザインシステム（カラーパレット、タイポグラフィ、コンポーネント）の作成を求められたとき
- 既存サイトの雰囲気を再現・参考にしたUIを実装するとき

## How to Use

### 1. サイト名が指定された場合

`references/` フォルダ内の該当ファイルを参照する。

```
references/stripe.md      → Stripe のデザインシステム
references/linear.app.md  → Linear のデザインシステム
references/notion.md       → Notion のデザインシステム
```

### 2. 雰囲気・色使いで指定された場合

下記カタログから最適なサイトを1〜3つ選び、そのリファレンスを参照して提案する。

### 3. デザインシステムの生成

リファレンスの構造（9セクション）に倣い、プロジェクト固有のデザインシステムを生成する：
1. Visual Theme & Atmosphere
2. Color Palette & Roles
3. Typography Rules
4. Component Stylings
5. Layout Principles
6. Depth & Elevation
7. Do's and Don'ts
8. Responsive Behavior
9. Agent Prompt Guide（色・フォントの即座参照用）

---

## Site Catalog

### Dark / Cinematic（ダーク・シネマティック）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| Linear | `references/linear.app.md` | ダーク, ミニマル, プロダクト, 開発ツール, 洗練 | Near-black `#08090a` |
| Framer | `references/framer.md` | ダーク, シネマティック, デザインツール, 黒 | Pure black `#000000` |
| Spotify | `references/spotify.md` | ダーク, 音楽, 没入感, 緑 | Dark `#121212`, Green `#1db954` |
| Supabase | `references/supabase.md` | ダーク, 開発者向け, エメラルド, 緑 | Dark `#0f0f0f`, Green `#3ecf8e` |
| Resend | `references/resend.md` | ダーク, シネマティック, メール, ラグジュアリー | Pure black `#000000` |
| SpaceX | `references/spacex.md` | ダーク, シネマティック, 宇宙, フルスクリーン | Black `#000000` |
| Raycast | `references/raycast.md` | ダーク, プレシジョン, ランチャー, 精密 | Dark blue `#07080a` |
| Warp | `references/warp.md` | ダーク, 温かい, ターミナル, フォレスト | Warm dark |
| Sentry | `references/sentry.md` | ダーク, パープル, 開発者ツール, モニタリング | Purple-black `#1f1633` |
| Sanity | `references/sanity.md` | ダーク, ノクターナル, CMS, 構造的 | Near-black `#0b0b0b` |
| RunwayML | `references/runwayml.md` | ダーク, 映画的, AI動画, エディトリアル | Dark editorial |
| Composio | `references/composio.md` | ダーク, サイバー, 開発者向け, シアン | Black + cyan |
| VoltAgent | `references/voltagent.md` | ダーク, ディープスペース, AI, エレクトリック | Near-black `#050507` |
| ClickHouse | `references/clickhouse.md` | ダーク, アシッドグリーン, DB, パフォーマンス | Black + yellow-green |

### Light / Clean（ライト・クリーン）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| Stripe | `references/stripe.md` | クリーン, フィンテック, 信頼感, パープル, グラデーション | White + purple gradient |
| Vercel | `references/vercel.md` | ミニマル, 白黒, 開発者向け, インフラ | White `#ffffff`, Black `#000` |
| Notion | `references/notion.md` | 温かい, ニュートラル, プロダクティビティ, シンプル | Warm white |
| Airbnb | `references/airbnb.md` | 温かい, 写真中心, マーケットプレイス, 赤 | White + Red `#ff385c` |
| Apple | `references/apple.md` | シネマティック, 白黒交互, プレミアム, 高級感 | Black/White alternating |
| Uber | `references/uber.md` | ミニマル, 白黒, 自信, ボールド | Black `#000000`, White |
| Figma | `references/figma.md` | カラフル, デザインツール, タイポグラフィ重視 | White + multicolor |
| Mintlify | `references/mintlify.md` | 白, エアリー, ドキュメント, 明快 | White, clean |
| Ollama | `references/ollama.md` | ミニマル, 白, AI, 究極のシンプル | Pure white |
| Expo | `references/expo.md` | 明るい, 開発者向け, モバイル, 洗練 | Luminous white |
| Lovable | `references/lovable.md` | 温かい, パーチメント, 優しい, クリーム | Cream `#f7f4ed` |
| Cal | `references/cal.md` | モノクロ, 白黒, スケジュール, Uber風 | White + black |

### Warm / Friendly（温かみ・フレンドリー）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| Claude | `references/claude.md` | 温かい, 知的, パーチメント, 文学的, ベージュ | Parchment `#f5f4ed` |
| Intercom | `references/intercom.md` | 温かい, エディトリアル, オレンジ, カスタマーサポート | Cream `#faf9f6`, Orange `#ff5600` |
| Clay | `references/clay.md` | 温かい, プレイフル, カラフル, クリーム | Warm cream + multicolor |
| Zapier | `references/zapier.md` | 温かい, フレンドリー, クリーム, 親しみやすい | Cream `#fffefb` |
| PostHog | `references/posthog.md` | 温かい, カジュアル, 反企業的, ユニーク | Warm, irreverent |
| Wise | `references/wise.md` | ボールド, ライムグリーン, フィンテック, 大胆 | Off-white + lime green |
| Pinterest | `references/pinterest.md` | 温かい, インスピレーション, 赤, ビジュアル | White + Red `#e60023` |
| Cursor | `references/cursor.md` | 温かい, ミニマル, オフホワイト, コードエディタ | Off-white `#f2f1ed` |
| Superhuman | `references/superhuman.md` | 白, ラグジュアリー, メール, ドラマティック | White + dramatic accent |

### Bold / Colorful（ビビッド・カラフル）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| Miro | `references/miro.md` | パステル, コラボレーション, カラフル, ジオメトリック | White + pastel accents |
| Webflow | `references/webflow.md` | リッチ, ブルー, ノーコード, マルチカラー | White + Blue `#146ef5` |
| Replicate | `references/replicate.md` | ボールド, ハイコントラスト, AI, フェスティバル | Bold, high-contrast |
| Mistral AI | `references/mistral.ai.md` | 温かい, アンバー, オレンジ, ヨーロッパ的 | Golden amber + orange |
| Revolut | `references/revolut.md` | ボールド, 大きいタイポ, フィンテック, 自信 | White + bold type |
| Kraken | `references/kraken.md` | パープル, クリプト, 信頼感 | White + Purple `#7132f5` |

### Enterprise / Professional（エンタープライズ・プロフェッショナル）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| IBM | `references/ibm.md` | エンタープライズ, Carbon, 構造的, ブルー | IBM Blue, Carbon system |
| NVIDIA | `references/nvidia.md` | ハイコントラスト, テクノロジー, グリーン, パワフル | Black + NVIDIA Green `#76b900` |
| BMW | `references/bmw.md` | プレミアム, 自動車, 精密, ドイツ的 | Dark + BMW Blue |
| HashiCorp | `references/hashicorp.md` | エンタープライズ, インフラ, クラウド | Enterprise tones |
| MongoDB | `references/mongodb.md` | ダークティール, データベース, フォレスト | Dark teal `#001e2b` |
| Airtable | `references/airtable.md` | エンタープライズ, シンプル, ブルー, スイス精密 | White + Blue `#1b61c9` |
| Coinbase | `references/coinbase.md` | クリーン, 信頼, クリプト, ブルー | White + Blue `#0052ff` |

### AI / Developer Tools（AI・開発者ツール）

| Site | File | Keywords | Primary Color |
|------|------|----------|---------------|
| ElevenLabs | `references/elevenlabs.md` | エレガント, 白, オーディオ, プレミアム | Near-white, minimal |
| Cohere | `references/cohere.md` | エンタープライズAI, クリーン, 信頼 | White, polished |
| Minimax | `references/minimax.md` | 白, 中国AI, プロダクトショーケース | White, clean |
| OpenCode | `references/opencode.ai.md` | モノスペース, ターミナル, ダーク・オン・ライト | Terminal aesthetic |
| Together AI | `references/together.ai.md` | パステル, グラデーション, エアリー, GPU | Pastel gradients |
| xAI | `references/x.ai.md` | ブルータリスト, モノスペース, ダーク, ミニマル | Dark, monospace |

---

## Reference File Structure

各リファレンスファイル（`references/*.md`）は以下の9セクション構成：

1. **Visual Theme & Atmosphere** — ムード、密度、デザイン哲学
2. **Color Palette & Roles** — セマンティックカラー名 + HEX + 機能的役割
3. **Typography Rules** — フォントファミリー、完全な階層テーブル
4. **Component Stylings** — ボタン、カード、入力、ナビゲーション（状態含む）
5. **Layout Principles** — スペーシングスケール、グリッド、余白の哲学
6. **Depth & Elevation** — シャドウシステム、サーフェス階層
7. **Do's and Don'ts** — デザインガードレールとアンチパターン
8. **Responsive Behavior** — ブレークポイント、タッチターゲット、折りたたみ戦略
9. **Agent Prompt Guide** — 色のクイックリファレンス、すぐ使えるプロンプト

---

## Implementation Workflow

### Step 1: サイト特定

ユーザーの指定に基づき、カタログからベストマッチを選ぶ。

**サイト名指定の場合:**
```
「Stripeのようなデザインで」→ references/stripe.md を読む
```

**雰囲気指定の場合:**
```
「ダークでモダンな開発者ツール風」→ Linear, Raycast, Supabase から選択
「温かくて親しみやすい」→ Claude, Notion, Zapier から選択
「高級感のあるミニマル」→ Apple, Uber, Superhuman から選択
```

**色指定の場合:**
```
「緑系」→ Supabase (#3ecf8e), Spotify (#1db954), NVIDIA (#76b900)
「パープル系」→ Stripe (gradient), Sentry (#1f1633), Kraken (#7132f5)
「青と白」→ Coinbase (#0052ff), Airtable (#1b61c9), Webflow (#146ef5)
```

### Step 2: リファレンス読み込み

選択したサイトの `references/<site>.md` を読み込み、以下を抽出:
- カラーパレット（HEX値）
- タイポグラフィ（フォント、サイズ、ウェイト）
- コンポーネントスタイル（ボタン、カード、入力）
- レイアウトルール（スペーシング、border-radius）

### Step 3: デザインシステム生成

プロジェクトに合わせてカスタマイズしたデザインシステムを生成:
- CSS変数 / Tailwind設定 / デザイントークン
- コンポーネントのスタイリング（React/Vue/HTML）
- レスポンシブ設定

### Step 4: 実装

デザインシステムに基づいてUIコンポーネントを実装:
- カラーテーマの適用
- タイポグラフィの設定
- コンポーネントの作成
- レイアウトの構築

---

## Quick Mood → Site Mapping

| Mood / Keyword | Best Match Sites |
|----------------|-----------------|
| ミニマル / minimal | Vercel, Uber, Ollama, Cal |
| ダーク / dark | Linear, Framer, SpaceX, Raycast |
| 温かい / warm | Claude, Notion, Cursor, Zapier |
| クリーン / clean | Stripe, Airbnb, Mintlify, Expo |
| プレミアム / premium | Apple, BMW, Superhuman, Resend |
| プレイフル / playful | Clay, PostHog, Miro, Replicate |
| エンタープライズ / enterprise | IBM, Airtable, HashiCorp, MongoDB |
| テクニカル / technical | Supabase, Sentry, ClickHouse, xAI |
| エディトリアル / editorial | Intercom, RunwayML, Lovable |
| ボールド / bold | Uber, Revolut, Wise, NVIDIA |
| パステル / pastel | Miro, Together AI, Clay |
| グラデーション / gradient | Stripe, Together AI, Expo |
| モノスペース / monospace | xAI, OpenCode, Composio |
| 白黒 / monochrome | Uber, Vercel, Cal, Apple |
| カラフル / colorful | Figma, Miro, Webflow, Clay |

---

## Anti-Patterns

- リファレンスの色をそのままコピーしない。ブランドカラーは参考にし、プロジェクト独自のパレットに変換する
- 複数サイトのスタイルを無秩序に混ぜない。ベースは1サイト、アクセントに別サイトの要素を取り入れる
- タイポグラフィのfont-familyをそのまま使わない（ライセンス注意）。Google Fonts等のオープンな代替を提案する
- レスポンシブブレークポイントは参照サイトそのままではなく、プロジェクトに最適化する
