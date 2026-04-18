# Design System: LINE (line.me)

> LINEのコーポレートサイト・プロダクトのデザイン仕様書。

---

## 1. Visual Theme & Atmosphere

クリーン、信頼感、大きくシンプルなタイポグラフィ。ゆったりとしたランディング型レイアウトで、body font-size 20px と大きめの設定が特徴。LINE Green をアクセントに、白背景を基調とした大胆でモダンなデザイン。

**Key Characteristics:**
- body font-size が 20px と非常に大きい
- 見出しは 60-70px でインパクト重視
- 韓国発サービスのため Noto Sans KR がフォールバックに含まれる
- CSS Custom Properties は未使用のシンプルな構成

---

## 2. Color Palette & Roles

### Primary

- **LINE Green** (`#06c755`): メインのブランドカラー。CTAボタン、アクセントに使用
- **LINE Green Dark** (`#05b34c`): ホバー・プレス時

### Neutral

- **Text Primary** (`#000000`): 本文テキスト
- **Text Secondary** (`#666666`): 補足テキスト、ラベル
- **Text Disabled** (`#999999`): 無効状態のテキスト
- **Border** (`#e5e5e5`): 区切り線、入力欄の枠
- **Background** (`#ffffff`): ページ背景
- **Surface** (`#f7f8f9`): カード、モーダル等の面

---

## 3. Typography Rules

### Font Family

- **Primary**: SFPro, Arial, "Noto Sans JP", "Noto Sans KR", sans-serif
- 韓国発サービスのため Noto Sans KR がフォールバックに含まれる

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Features | Notes |
|------|------|------|--------|-------------|----------------|----------|-------|
| Hero (EN) | SFPro | 70px | 700 | normal | normal | — | "Life on LINE" |
| Heading 2 (JP) | Noto Sans JP | 60px | 700 | 80px (x1.334) | normal | — | 大見出し |
| Body | SFPro/Noto Sans JP | 20px | 400 | normal | normal | — | 本文（非常に大きい） |

### CJK Typography

- **line-height**: normal（body）、1.27-1.334（見出し）
- **letter-spacing**: normal（全体統一）
- **palt**: 未適用
- **禁則処理**: word-break: break-all; overflow-wrap: break-word; line-break: strict;

---

## 4. Component Stylings

### Buttons

**Primary (LINE Green CTA)**
- Background: `#06c755`
- Text: `#ffffff`
- Padding: 12px 32px
- Border Radius: 8px
- Font Size: 16px
- Font Weight: 700

**Secondary**
- Background: transparent
- Text: `#000000`
- Border: 1px solid `#e5e5e5`
- Border Radius: 8px

### Inputs

- Background: `#ffffff`
- Border: 1px solid `#e5e5e5`
- Border (focus): 1px solid `#06c755`
- Border Radius: 8px
- Padding: 12px 16px
- Font Size: 16px
- Height: 48px

### Cards

- Background: `#ffffff`
- Border: 1px solid `#e5e5e5`
- Border Radius: 12px
- Padding: 24px
- Shadow: 0 2px 8px rgba(0,0,0,0.08)

---

## 5. Layout Principles

### Spacing Scale

| Token | Value |
|-------|-------|
| XS | 4px |
| S | 8px |
| M | 16px |
| L | 24px |
| XL | 40px |
| XXL | 64px |

### Container

- Max Width: 1120px
- Padding (horizontal): 24px
- Grid: 12 columns, 24px gutter

---

## 6. Depth & Elevation

| Level | Shadow | Usage |
|-------|--------|-------|
| 0 | none | フラットな要素 |
| 1 | `0 2px 8px rgba(0,0,0,0.08)` | カード、ドロップダウン |
| 2 | `0 4px 16px rgba(0,0,0,0.12)` | モーダル、ポップオーバー |
| 3 | `0 8px 24px rgba(0,0,0,0.16)` | ダイアログ、フローティング要素 |

---

## 7. Do's and Don'ts

### Do

- LINE Green `#06c755` をCTAやアクセントに一貫して使用する
- body font-size は 20px を維持する
- フォントは SFPro, Arial, Noto Sans JP, Noto Sans KR, sans-serif の順で指定
- 見出しは 60-70px の大きなサイズで大胆に表示する
- 韓国語フォールバック（Noto Sans KR）を含める

### Don't

- LINE Green 以外のブランドカラーをCTAに使わない
- body font-size を 20px 未満に変更しない
- palt を本文に適用しない
- CSS Custom Properties を独自に追加しない（実サイトでは未使用）

---

## 8. Responsive Behavior

### Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Mobile | <= 767px | モバイルレイアウト |
| Tablet | <= 1024px | タブレットレイアウト |
| Desktop | > 1024px | デスクトップレイアウト |

### Touch Targets

- 最小サイズ: 44px x 44px

### Font Size Adjustments

- モバイルでは本文 16-18px、見出しは 36-42px 程度に縮小

---

## 9. Agent Prompt Guide

### Quick Reference

```
Primary Color: #06c755 (LINE Green)
Text Color: #000000
Background: #ffffff
Font: SFPro, Arial, "Noto Sans JP", "Noto Sans KR", sans-serif
Body Size: 20px
Line Height: normal
CSS Custom Properties: なし
```

### Common Prompts

```
LINEのデザインシステムに従って、メッセージ一覧画面を作成してください。
- プライマリカラー: #06c755（LINE Green）
- フォント: SFPro, Arial, "Noto Sans JP", "Noto Sans KR", sans-serif
- 本文サイズ: 20px
- 行間: normal
- ボタン背景: #06c755、テキスト白、border-radius: 8px
- ボーダー: #e5e5e5
- 見出しは大きく（60-70px）、font-weight: 700
```
