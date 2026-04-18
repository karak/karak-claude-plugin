# Design System: クックパッド (cookpad.com)

> クックパッドのデザイン仕様書。温かみのある家庭的なデザインが特徴。

---

## 1. Visual Theme & Atmosphere

温かみのある家庭的なデザイン。料理と暮らしに寄り添う親しみやすさ。UGCメディア型で、レシピカードの一覧と詳細を行き来する構成。背景に温かみのあるオフホワイト `#f8f6f2` を使用し、純白を避けている。

**Key Characteristics:**
- 背景がオフホワイト `#f8f6f2`（純白ではない）
- letter-spacing: -0.4px を全要素に適用（詰め組み）
- 見出しの weight は 600（semibold）で統一（bold ではない）
- Adobe Fonts 版 noto-sans を使用
- font-feature-settings: "liga" で合字を有効化

---

## 2. Color Palette & Roles

### Primary

- **Cookpad Orange** (`#f28c06`): ブランドオレンジ。CTAボタン、ロゴに使用
- **Cookpad Orange Dark** (`#d97a00`): ホバー・プレス時

### Semantic

- **Danger** (`#e53935`): エラー、削除
- **Warning** (`#f9a825`): 警告、注意喚起
- **Success** (`#43a047`): 成功、完了

### Neutral

- **Text Primary** (`#0f0f0f`): 本文テキスト。ほぼ黒
- **Text Secondary** (`#757575`): 補足テキスト、ラベル
- **Text Disabled** (`#bdbdbd`): 無効状態のテキスト
- **Border** (`#e0e0e0`): 区切り線、入力欄の枠
- **Background** (`#f8f6f2`): ページ背景。温かみのあるオフホワイト
- **Surface** (`#ffffff`): カード、モーダル等の面

---

## 3. Typography Rules

### Font Family

- **Primary**: noto-sans, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, arial, sans-serif
- Adobe Fonts の noto-sans を最優先で指定

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Features | Notes |
|------|------|------|--------|-------------|----------------|----------|-------|
| Heading 1 | noto-sans | 18px | 600 | 28px (x1.556) | -0.4px | liga | セクション見出し |
| Heading 2 | noto-sans | 16px | 600 | 24px (x1.5) | -0.4px | liga | サブ見出し |
| Body | noto-sans | 16px | 400 | 24px (x1.5) | -0.4px | liga | 本文 |
| Label | noto-sans | 14px | 600 | 20px (x1.429) | -0.4px | liga | ラベル、ナビ |
| Caption | noto-sans | 12px | 400 | 16px (x1.333) | -0.4px | liga | 補足、投稿日時 |

### CJK Typography

- **line-height**: 1.5（本文）、1.333-1.556（見出し・キャプション）
- **letter-spacing**: -0.4px（全要素に適用。詰め組み）
- **palt**: 未使用
- **font-feature-settings**: "liga"（合字有効）
- **禁則処理**: word-break: break-all; overflow-wrap: break-word; line-break: strict;

---

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#f28c06`
- Text: `#ffffff`
- Padding: 8px 24px
- Border Radius: 8px
- Font Size: 14px
- Font Weight: 600

**Secondary**
- Background: transparent
- Text: `#0f0f0f`
- Border: 1px solid `#e0e0e0`
- Border Radius: 8px

### Inputs

- Background: `#ffffff`
- Border: 1px solid `#e0e0e0`
- Border (focus): 1px solid `#f28c06`
- Border Radius: 8px
- Padding: 8px 12px
- Font Size: 16px
- Height: 40px

### Cards

- Background: `#ffffff`
- Border: 1px solid `#e0e0e0`
- Border Radius: 12px
- Padding: 16px
- Shadow: `0 1px 3px rgba(0,0,0,0.08)`

---

## 5. Layout Principles

### Spacing Scale

| Token | Value |
|-------|-------|
| XS | 4px |
| S | 8px |
| M | 16px |
| L | 24px |
| XL | 32px |
| XXL | 48px |

### Container

- Max Width: 1080px
- Padding (horizontal): 16px
- Grid: レシピ一覧は 2-4列（レスポンシブ）、Gutter 16px

---

## 6. Depth & Elevation

| Level | Shadow | Usage |
|-------|--------|-------|
| 0 | none | フラットな要素 |
| 1 | `0 1px 3px rgba(0,0,0,0.08)` | レシピカード |
| 2 | `0 4px 8px rgba(0,0,0,0.1)` | ドロップダウン、ポップオーバー |
| 3 | `0 8px 24px rgba(0,0,0,0.15)` | モーダル、ダイアログ |

---

## 7. Do's and Don'ts

### Do

- font-family は noto-sans を先頭に、system-ui フォールバックチェーンを指定する
- letter-spacing: -0.4px を全体に適用する（クックパッドの詰め組み）
- 背景色は #f8f6f2（温かみのあるオフホワイト）を使用する
- 見出しの weight は 600（semibold）で統一する
- font-feature-settings: "liga" を適用する

### Don't

- 背景に純白 #ffffff を使わない（温かみが失われる）
- テキスト色に純粋な #000000 を使わない（#0f0f0f を使用）
- letter-spacing を 0 や正の値にしない（全体が -0.4px で統一）
- 見出しに font-weight: 700 (bold) を使わない（600 semibold が正しい）

---

## 8. Responsive Behavior

### Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Mobile | <= 767px | モバイルレイアウト |
| Tablet | <= 1023px | タブレットレイアウト |
| Desktop | > 1024px | デスクトップレイアウト |

### Touch Targets

- 最小サイズ: 44px x 44px

### Font Size Adjustments

- モバイルでは本文 14-16px、見出しはデスクトップの 80% 程度に縮小

---

## 9. Agent Prompt Guide

### Quick Reference

```
Primary Color: #f28c06 (Cookpad Orange)
Text Color: #0f0f0f
Background: #f8f6f2 (warm off-white)
Font: noto-sans, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, arial, sans-serif
Body Size: 16px
Line Height: 1.5
Letter Spacing: -0.4px
Font Feature: "liga"
Heading Weight: 600
```

### Common Prompts

```
クックパッドのデザインシステムに従って、レシピ一覧カードを作成してください。
- プライマリカラー: #f28c06（オレンジ）
- 背景色: #f8f6f2（温かみのあるオフホワイト）
- フォント: noto-sans, system-ui 系フォールバック
- 行間: line-height: 1.5
- 字間: letter-spacing: -0.4px
- 見出し: 600 (semibold)
- カード背景: #fff、border-radius: 12px
- font-feature-settings: "liga"
```
