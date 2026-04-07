# Design System: SmartHR (smarthr.jp)

> SmartHR Design System（https://smarthr.design/）の公式デザイントークンに基づく。

---

## 1. Visual Theme & Atmosphere

クリーンで信頼感のある業務UI。装飾を排し、コンテンツと操作性を優先するミニマルなデザイン。ウォームグレー（Stone系）を基調とした柔らかいニュートラルカラーが特徴で、純粋なグレーではなく暖色寄りのトーン。

**Key Characteristics:**
- 業務アプリケーション向けの情報密度の高いUI
- Stone 系ウォームグレーによる柔らかい色彩
- Windows での游ゴシック表示を `@font-face` で最適化
- ブランドカラー `#00c4cc` とプロダクトカラー `#0077c7` を明確に使い分け

---

## 2. Color Palette & Roles

### Primary

- **SmartHR Blue** (`#00c4cc`): ブランドアイデンティティ。ロゴ、イラスト、チャート用。UIテキストには非推奨（コントラスト不足）
- **Product Main** (`#0077c7`): プロダクトUIのプライマリカラー。ボタン、アクティブ状態、フォーカスリング

### Semantic

- **Danger** (`#e01e5a`): エラー、削除操作、バリデーションエラー
- **Warning** (`#ffcc17`): 警告、注意喚起

### Interactive

- **Text Link** (`#0071c1`): テキストリンクの色
- **Orange Accent** (`#ff9900`): アクセントカラー、注目を引く要素

### Neutral — Stone Scale（ウォームグレー）

- **Text Black** (`#23221e`): 本文テキスト、見出し
- **Text Grey** (`#706d65`): 補足テキスト、セカンダリラベル
- **Text Disabled** (`#c1bdb7`): 無効状態のテキスト
- **Stone 01** (`#f8f7f6`): ページ背景
- **Stone 02** (`#edebe8`): テーブルヘッダー背景
- **Stone 03** (`#aaa69f`): 補助的なボーダー、アイコン
- **Stone 04** (`#4e4c49`): 濃いグレーテキスト

### Surface & Borders

- **White** (`#ffffff`): コンポーネントのベース背景
- **Border** (`#d6d3d0`): 区切り線、入力欄の枠
- **Over Background** (`#f2f1f0`): BACKGROUND 上のグルーピング面

### Chart Colors

- `#00c4cc`, `#ffcd00`, `#ff9100`, `#e65537`, `#2d4b9b`, `#2d7df0`, `#69d7ff`, `#4bb47d`, `#05878c`

---

## 3. Typography Rules

### Font Family

- **Primary**: AdjustedYuGothic, "Yu Gothic", YuGothic, "Hiragino Sans", sans-serif
- Windows での游ゴシック Medium を通常ウェイトにマッピングする `@font-face` トリック必須

```css
@font-face {
  font-family: AdjustedYuGothic;
  font-weight: 400;
  src: local("Yu Gothic Medium");
}
@font-face {
  font-family: AdjustedYuGothic;
  font-weight: 700;
  src: local("Yu Gothic Bold");
}
```

### Hierarchy

| Role | Token | Size | Weight | Line Height | Letter Spacing | Features | Notes |
|------|-------|------|--------|-------------|----------------|----------|-------|
| Display | XXL | 2rem (32px) | 700 | 1.25 | 0 | — | ページタイトル |
| Heading 1 | XL | 1.5rem (24px) | 700 | 1.25 | 0 | — | セクション見出し |
| Heading 2 | L | 1.2rem (19.2px) | 700 | 1.5 | 0 | — | サブ見出し |
| Body | M | 1rem (16px) | 400 | 1.5 | 0 | — | 本文（標準） |
| Small | S | 0.857rem (13.7px) | 400 | 1.5 | 0 | — | 補足テキスト |
| Caption | XS | 0.75rem (12px) | 400 | 1.5 | 0 | — | キャプション、注釈 |
| Smallest | XXS | 0.667rem (10.7px) | 400 | 1.5 | 0 | — | バッジ、ラベル |

### CJK Typography

- **line-height**: 1.5（NORMAL）、見出し 1.25（TIGHT）、コードブロック 1.75（RELAXED）
- **letter-spacing**: 0（デフォルト）
- **禁則処理**: overflow-wrap: break-word;（ブラウザデフォルトに依存）

---

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#0077c7`
- Text: `#ffffff`
- Border Radius: 6px
- Font Size: 1rem (16px)
- Font Weight: 700
- Padding: 8px 16px

**Secondary**
- Background: transparent
- Text: `#0077c7`
- Border: 1px solid `#0077c7`
- Border Radius: 6px

**Danger**
- Background: `#e01e5a`
- Text: `#ffffff`
- Border Radius: 6px

### Inputs

- Background: `#ffffff`
- Border: 1px solid `#d6d3d0`
- Border (focus): 2px solid `#0077c7`
- Border Radius: 6px
- Font Size: 1rem (16px)
- Padding: 8px 12px

### Tables

- Header Background: `#edebe8`
- Row Background: `#ffffff`
- Row Background (alternate): `#f8f7f6`
- Border: 1px solid `#d6d3d0`

---

## 5. Layout Principles

### Spacing Scale (8px base)

| Token | Value |
|-------|-------|
| XS | 4px (0.25rem) |
| S | 8px (0.5rem) |
| M | 16px (1rem) |
| L | 24px (1.5rem) |
| XL | 32px (2rem) |
| XXL | 40px (2.5rem) |

### Container

- プロダクトUI: 全幅（サイドバー + メインコンテンツ構成）

---

## 6. Depth & Elevation

| Level | Shadow | Usage |
|-------|--------|-------|
| 0 | none | フラットな要素 |
| 1 | `0 2px 4px rgba(0,0,0,0.1)` | カード、ドロップダウン |
| 2 | `0 4px 8px rgba(0,0,0,0.15)` | モーダル、ダイアログ |

---

## 7. Do's and Don'ts

### Do

- Windows での游ゴシック表示には必ず `AdjustedYuGothic` の `@font-face` トリックを使う
- テキストカラーは `#23221e`（Text Black）を使い、純粋な `#000000` は避ける
- ニュートラルカラーは Stone 系（ウォームグレー）を使用する
- ブランドカラー `#00c4cc` はイラスト・チャート用とし、UIの操作要素には `#0077c7` を使う
- アクセシビリティを重視し、WCAG AA 以上のコントラスト比を確保する

### Don't

- ブランドカラー `#00c4cc` をテキストや小さなUI要素に使わない（白背景でコントラスト不足）
- 游ゴシックを `@font-face` なしで `font-weight: 400` 指定しない（Windows で細く表示される）
- 純粋なグレー（`#808080` 等）を使わない。Stone 系のウォームグレーを使う
- テキストリンクの色を `#0077c7` と混同しない。リンクは `#0071c1`

---

## 8. Responsive Behavior

### Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| SP | <= 599px | スマートフォン |
| Tablet | 600px-959px | タブレット |
| Desktop | >= 960px | デスクトップ |

### Touch Targets

- 最小サイズ: 44px x 44px

---

## 9. Agent Prompt Guide

### Quick Reference

```
Brand Color: #00c4cc（ロゴ・チャート用、UIには使わない）
Product Main: #0077c7
Text Color: #23221e
Text Secondary: #706d65
Link Color: #0071c1
Background: #f8f7f6
Surface: #ffffff
Border: #d6d3d0
Danger: #e01e5a
Font: AdjustedYuGothic, "Yu Gothic", YuGothic, "Hiragino Sans", sans-serif
Body Size: 16px (1rem)
Line Height: 1.5
```

### Common Prompts

```
SmartHR のデザインシステムに従って、従業員一覧テーブルを作成してください。
- フォント: AdjustedYuGothic, "Yu Gothic", YuGothic, "Hiragino Sans", sans-serif
- テキスト色: #23221e
- テーブルヘッダー背景: #edebe8
- ボーダー: 1px solid #d6d3d0
- プライマリボタン: 背景 #0077c7、テキスト #ffffff、角丸 6px
- 行間: line-height: 1.5
- @font-face で游ゴシック Medium を 400 にマッピングすること
```
