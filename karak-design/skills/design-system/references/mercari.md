# Design System: メルカリ (mercari.com/jp)

> このファイルはAIエージェントが正確な日本語UIを生成するためのデザイン仕様書です。

---

## 1. Visual Theme & Atmosphere

クリーン、ミニマル、白背景ベースの実用志向UI。商品一覧のグリッド表示は情報密度が高いが、余白は十分に確保されている。CSSフレームワークに Panda CSS を採用。

**Key Characteristics:**
- body font-size が 15px（一般的な 16px ではない）
- 全体の line-height が x1.4 で統一されており、日本語サイトとしてはタイト
- 見出しの色が `#666666` でメイン `#333333` より薄い珍しいパターン
- フォント指定に「Custom」サフィックス付きの独自 @font-face 定義を使用

---

## 2. Color Palette & Roles

### Primary

- **Mercari Red** (`#ff333f`): メインのブランドカラー。CTAボタン、アクティブタブに使用

### Semantic

- **Link** (`#0073cc`): テキストリンク

### Neutral

- **Text Primary** (`#333333`): 本文テキスト、フッターテキスト
- **Text Secondary** (`#666666`): 見出し（h2）、非アクティブタブ、補足テキスト
- **Background** (`#ffffff`): ページ背景

---

## 3. Typography Rules

### Font Family

- **Primary**: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN Custom", "Hiragino Sans Custom", "Meiryo Custom", sans-serif
- 「Custom」サフィックス付きの独自 @font-face 定義。フォントメトリクスを調整している

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Features | Notes |
|------|------|------|--------|-------------|----------------|----------|-------|
| Heading 2 | 本文と同じ | 20px | 700 | 28px (x1.4) | normal | — | 色 #666666 |
| Heading 3 | 本文と同じ | 17px | 700 | 23.8px (x1.4) | normal | — | 色 #333333 |
| Body | 本文と同じ | 15px | 400 | 21px (x1.4) | normal | — | 色 #333333 |
| Footer | 本文と同じ | 15px | 700 | 21px | normal | — | 色 #333333 |
| Link | 本文と同じ | 15px | 400 | — | normal | — | 色 #0073cc |
| CTA Button | 本文と同じ | 14px | 700 | — | normal | — | 色 #fff / bg #ff333f |
| Tab (active) | 本文と同じ | 14px | 700 | — | normal | — | 色 #ff333f |
| Tab (inactive) | 本文と同じ | 14px | 700 | — | normal | — | 色 #666 |
| Input | 本文と同じ | 16px | 400 | 22.4px | normal | — | 検索入力欄 |

### CJK Typography

- **line-height**: x1.4（全要素統一。日本語としてはタイト寄り）
- **letter-spacing**: normal（全要素。日本語の字間調整なし）
- **palt**: 未使用
- **禁則処理**: word-break: normal; overflow-wrap: break-word;

---

## 4. Component Stylings

### Buttons

**Primary (CTA)**
- Background: `#ff333f`
- Text: `#ffffff`
- Border Radius: 4px
- Font Size: 14px
- Font Weight: 700

**Secondary**
- Background: `#ffffff`
- Text: `#333333`
- Border Radius: 4px
- Font Size: 14px
- Font Weight: 400

### Tabs

**Active**
- Text: `#ff333f`
- Font Weight: 700

**Inactive**
- Text: `#666666`
- Font Weight: 700

### Inputs

- Background: `#ffffff`
- Border Radius: 0px（角丸なし）
- Font Size: 16px（iOS ズーム防止）

---

## 5. Layout Principles

### Spacing (CSS Custom Properties)

| Token | Value | Usage |
|-------|-------|-------|
| --grid-layout-gutter | 24px | グリッド間の余白 |
| --grid-layout-inset | 16px | グリッド内側の余白 |
| --grid-layout-page-padding-top | 40px | ページ上部パディング |
| --grid-layout-page-padding-bottom | 64px | ページ下部パディング |
| --grid-layout-page-padding-horizontal | 36px | ページ左右パディング |

---

## 6. Depth & Elevation

### z-index 階層

| Token | Value | Usage |
|-------|-------|-------|
| --mer-z-index-menu | 1100 | メニュー |
| --mer-z-index-navigation | 1200 | ナビゲーション |
| --mer-z-index-modal | 1400 | モーダル |
| --mer-z-index-snackbar | 1500 | スナックバー通知 |
| --mer-z-index-tooltip | 1600 | ツールチップ |

---

## 7. Do's and Don'ts

### Do

- ブランドカラー `#ff333f` はCTAとアクティブ状態にのみ使用する
- body の font-size は 15px を守る（16px にしない）
- line-height は x1.4 で統一する
- フォント指定の「Custom」サフィックスを維持する
- ボタンの角丸は 4px に統一する
- 見出しには `#666666` を使用し、本文 `#333333` と差をつける

### Don't

- `#ff333f` を背景色やテキスト色として多用しない（CTA・アクティブ状態専用）
- letter-spacing を追加しない（全要素で normal）
- palt を適用しない
- line-height を x1.4 以外に変えない

---

## 8. Responsive Behavior

### Touch Targets

- 最小サイズ: 44px x 44px（WCAG基準）

### Font Size Adjustments

- 入力欄は 16px を維持（iOS のズーム防止）
- 本文は 15px を基準とし、モバイルでも変更しない

---

## 9. Agent Prompt Guide

### Quick Reference

```
Primary Color: #ff333f (Mercari Red)
Link Color: #0073cc
Text Color: #333333
Text Secondary: #666666
Background: #ffffff
Font: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN Custom", "Hiragino Sans Custom", "Meiryo Custom", sans-serif
Body Size: 15px
Line Height: 1.4
Letter Spacing: normal
palt: なし
CSS Framework: Panda CSS
```

### Common Prompts

```
メルカリのデザインシステムに従って、商品一覧ページを作成してください。
- プライマリカラー（CTAのみ）: #ff333f
- リンク色: #0073cc
- フォント: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN Custom", "Hiragino Sans Custom", "Meiryo Custom", sans-serif
- 本文: 15px / 400 / line-height: 1.4 / color: #333333
- 見出し: 20px / 700 / line-height: 1.4 / color: #666666
- グリッド余白: 24px
- ボタン角丸: 4px
```
