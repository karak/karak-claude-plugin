# Design System: freee (freee.co.jp)

> freee Vibes Design System（https://vibes.freee.co.jp/）の公式デザイントークンおよびコーポレートサイトに基づく。

---

## 1. Visual Theme & Atmosphere

親しみやすく、明快な業務UI。複雑な会計・人事業務を、直感的で軽やかなインターフェースで提供する。ブルーを基調としたクリーンな配色で、プロダクトUI（Vibes）とコーポレートサイトで異なるフォント戦略を持つ。

**Key Characteristics:**
- プロダクトUIはシステムフォント、コーポレートサイトは Noto Sans JP（Google Fonts）
- 見出しの weight は 500（medium）が基本で、700（bold）は強調時のみ
- Vibes Design System はピル型ボタン（99rem）、コーポレートサイトは角丸 8px
- 4px ベースのスペーシングスケール

---

## 2. Color Palette & Roles

### Primary

- **Primary Blue** (`#2864f0`): メインのブランドカラー。CTAボタン、リンク、アクティブ状態
- **Primary Hover** (`#285ac8`): ホバー時
- **Primary Dark** (`#1e46aa`): プレス時・ダーク系アクセント
- **Primary Darkest** (`#143278`): 最も暗いブルー

### Blue Scale

- `#ebf3ff` → `#dce8ff` → `#aac8ff` → `#73a5ff` → `#2864f0` → `#3264dc` → `#285ac8` → `#1e46aa` → `#23418c` → `#143278`

### Semantic

- **Danger** (`#dc1e32`): エラー、削除、バリデーションエラー
- **Warning** (`#ffb91e`): 警告、注意喚起
- **Success** (`#00963c`): 成功、完了
- **Orange** (`#fa6414`): 通知、アクセント

### Neutral

- **Text Primary** (`#323232`): 見出し、本文テキスト
- **Text Body** (`#595959`): body デフォルトテキスト色
- **Text Muted** (`#8c8989`): プレースホルダー、ラベル
- **Heading Blue** (`#1e46aa`): h3 見出し、キャプション強調

### Surface & Borders

- **White** (`#ffffff`): コンポーネントのベース背景
- **Background Light** (`#f7f5f5`): カード背景、セクション背景
- **Border** (`#e9e7e7`): 区切り線、ボーダー
- **Input Border** (`#e1dcdc`): フォーム入力欄の枠

---

## 3. Typography Rules

### Font Family

**プロダクトUI（Vibes）:**
```css
font-family: '-apple-system', BlinkMacSystemFont, 'Helvetica Neue',
  'ヒラギノ角ゴ ProN', 'Hiragino Kaku Gothic ProN', Arial,
  'メイリオ', Meiryo, sans-serif;
```

**コーポレートサイト:**
```css
font-family: "Noto Sans JP", sans-serif;
```

### Hierarchy — プロダクトUI (Vibes)

| Role | Token | Size | Weight | Line Height | Letter Spacing | Features | Notes |
|------|-------|------|--------|-------------|----------------|----------|-------|
| Heading 1 | FontSize1500 | 1.5rem (24px) | 700 | 1.5 | 0 | — | ページタイトル |
| Heading 2 | FontSize1000 | 1rem (16px) | 700 | 1.5 | 0 | — | セクション見出し |
| Heading 3 | FontSize0875 | 0.875rem (14px) | 700 | 1.5 | 0 | — | サブ見出し |
| Body | FontSize0875 | 0.875rem (14px) | 400 | 1.5 | 0 | — | 本文（標準） |
| Caption | FontSize0750 | 0.75rem (12px) | 400 | 1.5 | 0 | — | キャプション |

### Hierarchy — コーポレートサイト

| Role | Size | Weight | Line Height | Letter Spacing | Color | Notes |
|------|------|--------|-------------|----------------|-------|-------|
| H2 (hero) | 40px | 500 | x1.5 | 0.04em | `#323232` | ヒーローセクション |
| H2 | 34px | 500/700 | x1.5 | 0.04em | `#323232` | セクション見出し |
| H3 | 24px | 500/700 | x1.5 | normal | `#1e46aa` | サブ見出し（ブルー） |
| Body | 16px | 400 | x1.5 | normal | `#323232` | 本文 |
| Nav Link | 14px | 400 | x1.5 | normal | `#323232` | ヘッダーナビ |

### CJK Typography

- **line-height**: 1.5（全体統一、Vibes・コーポレート共通）
- **letter-spacing**: コーポレートサイト大見出し 0.04em-0.05em、その他 normal
- **palt**: 未使用
- **禁則処理**: overflow-wrap: break-word;

---

## 4. Component Stylings

### Buttons

**Primary (コーポレートサイト)**
- Background: `#2864f0`
- Text: `#ffffff`
- Border: 2px solid `#2864f0`
- Border Radius: 8px
- Font Size: 16px
- Font Weight: 500/700

**Secondary**
- Background: `#ffffff`
- Text: `#2864f0`
- Border: 1px solid `#2864f0`
- Border Radius: 5px

**Danger**
- Background: `#dc1e32`
- Text: `#ffffff`
- Border Radius: 8px

### Inputs

- Background: `#ffffff`
- Border: 1px solid `#cccccc`
- Border Radius: 4px
- Font Size: 16px
- Placeholder: weight 300, color `#8c8989`

### Cards

- Background: `#ffffff`
- Border Radius: 0.75rem (12px)
- Shadow: `0 0 1rem rgba(0,0,0,0.1), 0 0.125rem 0.25rem rgba(0,0,0,0.2)`

---

## 5. Layout Principles

### Spacing Scale (Vibes)

| Token | Value |
|-------|-------|
| XSmall | 0.25rem (4px) |
| Small | 0.5rem (8px) |
| Basic | 1rem (16px) |
| Large | 1.5rem (24px) |
| XLarge | 2rem (32px) |
| XXLarge | 3rem (48px) |

### Border Radius Scale (Vibes)

| Token | Value | Usage |
|-------|-------|-------|
| Base | 0.5rem (8px) | 入力欄、基本要素 |
| Card | 0.75rem (12px) | カード |
| Floating | 1rem (16px) | ポップアップ |
| Dialog | 1.5rem (24px) | ダイアログ |
| Full | 99rem | ピル型ボタン |

### Container

- Max Width: 70rem (1120px)

---

## 6. Depth & Elevation

| Level | Shadow | Usage |
|-------|--------|-------|
| Card | `0 0 1rem rgba(0,0,0,0.1), 0 0.125rem 0.25rem rgba(0,0,0,0.2)` | カード |
| Floating | `0 0 1.5rem rgba(0,0,0,0.1), 0 0.25rem 0.5rem rgba(0,0,0,0.2)` | フローティング要素 |
| Popup | `0 0 2rem rgba(0,0,0,0.1), 0 0.375rem 0.75rem rgba(0,0,0,0.2)` | ポップアップ |

- すべてデュアルシャドウ（広い拡散 + 近い影）構成

---

## 7. Do's and Don'ts

### Do

- プロダクトUIとコーポレートサイトでフォント戦略が異なることを認識する
- プロダクトUIにはシステムフォントスタック（Vibes）を使う
- コーポレートサイトのボタンは border-radius: 8px
- 見出しの weight は 500（medium）を基本とし、強調時のみ 700
- スペーシングは 4px の倍数に揃える
- WCAG AA 以上のコントラスト比を確保する

### Don't

- コーポレートサイトのフォント（Noto Sans JP）をプロダクトUIに使わない
- テキスト色に純粋な `#000000` を使わない。`#323232` を使用する
- ブランドブルー `#2864f0` の上に暗い色のテキストを置かない
- body のデフォルトテキスト色は `#595959`（`#323232` は見出し・強調用）

---

## 8. Responsive Behavior

### Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Narrow Mobile | <= 375px | 狭いモバイル |
| Mobile | <= 768px | モバイル |
| Tablet | <= 1024px | タブレット |
| Desktop | > 1024px | デスクトップ |

### Touch Targets

- 最小サイズ: 36px（Vibes デフォルト）

---

## 9. Agent Prompt Guide

### Quick Reference

```
Primary Color: #2864f0
Heading Blue: #1e46aa
Text Heading: #323232
Text Body: #595959
Background: #ffffff
Border: #e9e7e7
Danger: #dc1e32
Success: #00963c

Product UI Font: '-apple-system', BlinkMacSystemFont, 'Helvetica Neue',
  'ヒラギノ角ゴ ProN', 'Hiragino Kaku Gothic ProN', Arial,
  'メイリオ', Meiryo, sans-serif
Website Font: "Noto Sans JP", sans-serif

Body Size (Product): 14px
Body Size (Website): 16px
Line Height: 1.5
Heading Weight: 500 (medium)
Button Radius (Website): 8px
Button Radius (Product): 99rem (pill)
```

### Common Prompts

```
freee のコーポレートサイト風に、請求書一覧画面を作成してください。
- フォント: "Noto Sans JP", sans-serif
- テキスト色: #595959（body）、#323232（見出し・強調）
- 見出し: weight 500、大見出し（34px以上）は letter-spacing: 0.04em
- h3: #1e46aa（ブルー）
- プライマリボタン: 背景 #2864f0、テキスト #fff、角丸 8px
- 入力欄: ボーダー #cccccc、角丸 4px
- スペーシング: 4px の倍数
```
