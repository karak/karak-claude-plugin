---
name: mobile-auth-screen-design
description: "MUST USE for any mobile auth screen UI question. This skill contains a specialized checklist covering 5 areas that general design advice misses: (1) scroll / safe-area layout patterns that cause keyboard occlusion on iOS and Android, (2) Google and Apple brand-guideline compliance for social login buttons, (3) touch target sizing standards for password toggle and auth controls, (4) CTA vs input-field visual hierarchy — fill color, shadow, icon, size, border-radius as equally-weighted methods, and (5) platform-specific patterns for SwiftUI / Jetpack Compose / React Native. Apply whenever the user is reviewing, building, or troubleshooting a login, signup, registration, or password-reset screen — regardless of whether they frame it as a design question, a layout problem, a usability complaint, or an implementation question. Proactively trigger; do not wait for an explicit design review request."
---

# Mobile Auth Screen Design Checklist

モバイルログイン/認証画面をモダンなデザインパターンと照合するチェックリスト。

## レビューの進め方

1. **コードや仕様から数値を読み取る** — 高さ・パディング・フォントサイズを実際のコードから抽出して比較する
2. **必須チェックを先に走査** — 下記の「最初に確認する5点」は必ずチェックする
3. **欠けている要素にも気づく** — 実装にないが本来あるべき要素（パスワード忘れリンクなど）を指摘する
4. **数値で修正案を提示** — 「大きくする」ではなく「44px → 56px」の形で具体化する
5. **コードがある場合は修正コードを示す** — React Native / SwiftUI / Compose それぞれの言語で

---

## 最初に確認する5点（ほぼ必ず問題がある）

### ① フォームの垂直配置（設計思想のアンチパターン）

`justifyContent: 'center'` / `Alignment.Center` / `VStack` の垂直中央配置は **PCデザインの移植であり、モバイルではアンチパターン**。

理由: ソフトウェアキーボード（画面の約50%を占有）が出現するとフォームが上に押し出され、CTAボタンが隠れる。さらに画面上部への視線移動が自然なモバイルの読み方と逆行する。

✅ 正しい配置: フォームを画面上部1/3〜1/2に配置し、下部に余白を確保する。

### ② CTA ボタンとフィールドの視覚的階層

フィールドとボタンの区別が曖昧だと「どれを押せばいいか」が伝わらない。以下の手段を**同等の価値として並列に**評価し、いずれかが確保されているかを確認する：

| 手段 | 例 |
|------|----|
| 塗りつぶし色 | ボタンに濃色・鮮色の背景、フィールドは枠線のみ |
| シャドウ / elevation | `shadowColor` + `shadowOpacity` / `elevation: 4` |
| アイコン + テキスト | 動詞アイコン（→, ✓ など）でCTAと明示 |
| サイズ差 | フィールドより大きい（目安: 8px以上の差） |
| 角丸の差 | フィールド 8px / ボタン 16px や pill 型 |

**判定方法 — コードから以下を全て読んで総合評価する：**
- `height` の数値比較
- `backgroundColor` / `background(Color...)` の有無と色
- `shadowColor` / `elevation` の有無
- アイコン（`Image`、絵文字、`Text`）の有無

**要改善の例:** フィールド `height:44`・ボタン `height:48`、かつどちらも `borderWidth:1` でフラット → 差別化ゼロ

**問題なしの例:** フィールド `height:52`・ボタン `height:52`、かつボタンに濃色塗りつぶし＋シャドウ＋アイコン → 高さは同じでも視覚的階層は十分

### ③ 「パスワードを忘れた」リンクの欠如と配置

ほとんどの実装で見落とされる。**存在しない場合は必ず指摘する。**

✅ 正しい配置: パスワードフィールドの**直下・右寄せ**（フォーム最下部への配置は発見率が低い）

### ④ Google ボタンのブランドガイドライン違反

テキストのみの Google ボタンは **Google Brand Guidelines 違反**。G ロゴ（SVG）の表示が必須。App Store / Play Store 審査でのリジェクト原因になる。

✅ 正しい実装: G ロゴ + "Google で続ける" テキストを組み合わせる。

### ⑤ パスワード表示/非表示トグルの欠如

`secureTextEntry` / `.secureField` のみでトグルなしは、モバイルでの入力ミス頻発の原因。特に「パスワード確認」フィールドが存在する場合は必須。

---

## チェックリスト全項目（A–J）

### A. レイアウト・構造

- **A-1** フォームは画面上部1/3〜1/2に配置。垂直中央（`justifyContent:center` 等）は**キーボード表示時にフォームが隠れるアンチパターン**
- **A-2** タイトルとフォームは上寄せ
- **A-3** 小型端末（SE等）での ScrollView 対応 *(実装時)*
- **A-4** KeyboardAvoidingView / WindowInsets 対応 *(実装時)*
- **A-5** 水平パディング: **24–32px**（16–20px は狭い）
- **A-6** セクション間ギャップ階層: タイトル→フィールド **32–40px** / フィールド→ボタン **24–32px** / ボタン→OAuth **24–32px**
- **A-7** フィールド間ギャップ: **16–20px**（12px は狭すぎる）
- **A-8** CTA 下の余白を確保

### B. タイトル・ブランディング

- **B-1** 画面上部にアプリロゴ *(検討)*
- **B-2** タイトルサイズ: **28–36px**
- **B-3** サブタイトル/説明文を追加（例:「登録済みのメールアドレスを入力してください」）— **パスワードリセット画面では特に重要**
- **B-4** タイトルは左揃えが主流 *(検討)*

### C. 入力フィールド

- **C-2** ラベルフォント: **13–14px**、通常ケース。`uppercase + wide tracking` は PC 向き
- **C-3** ラベルの言語をアプリの言語に統一
- **C-4** フィールド高さ: **52–56px**（44–46px は低い）
- **C-7** 枠線太さ: **1.5–2px**（1px は視認性が低い）
- **C-10** 入力アイコン: メール(✉)・鍵(🔒)をフィールド左に配置
- **C-11** パスワード表示/非表示トグル — モバイルでは必須

### D. ボタン (CTA)

- **D-1** プライマリ CTA の視覚的優先度: フィールドとの差別化が必須。塗りつぶし色・シャドウ・アイコン・サイズ差・角丸差のいずれか（複数組み合わせが理想）で実現する。**`height` 単独で判断せず、`backgroundColor`・`shadowColor`・アイコン有無を総合評価する**
- **D-3** ボタンの角丸でフィールドと差別化: フィールド 8–10px / ボタン 12–16px 以上
- **D-4** ドロップシャドウでボタンを浮かせ、フィールドと区別
- **D-8** サイズ段階差: フィールド(M) → CTA(L) の明確な差

### E. ソーシャルログイン

- **E-1** Google ボタンに **G ロゴ必須**（テキストのみは Brand Guidelines 違反・審査リジェクトリスク）
- **E-5** 区切り線: 「または」ラベル付き divider、上下 24–32px
- **E-6** App Store 提出時: ソーシャルログインがある場合 Apple Sign In 必須 *(検討)*

### F. リンク・テキスト

- **F-1** 「パスワードを忘れた」: **実装されていない場合は必ず指摘。** 配置はパスワードフィールド**直下・右寄せ**
- **F-2** タッチターゲット: **44px 以上**
- **F-4** アカウント作成リンク: 「アカウントをお持ちでない方？**新規登録**」の構成
- **F-5** リンク色はアクセントカラー（#666 グレーのままにしない）

### G. エラー・バリデーション

- **G-1** エラー時はフィールド枠線をオレンジ/赤に変化
- **G-2** ⚠️ アイコンをエラーメッセージに添付
- **G-6** **色だけに依存しない** — 色覚多様性ユーザーに届かない。アイコン + テキスト + 枠線色の複数チャネル必須

### H. タイポグラフィ

- **H-2** 本文フォントサイズ: **16px 以上**（Apple HIG 推奨最小）
- **H-3** ラベルの uppercase + 12px はデスクトップ向き

### I. アクセシビリティ・UX（実装時）

- **I-2** 全インタラクティブ要素 **44×44pt 以上**
- **I-6** `autoComplete="email"` / `.textContentType(.emailAddress)` / `keyboardType(.emailAddress)` を設定
- **I-7** `type="email"` / `.keyboardType(.emailAddress)` で @ キーボード表示

### J. ビジュアル・ポリッシュ

- **J-4** 要素サイズに明確な段階差（S/M/L/XL）
- **J-5** 全認証画面でスタイルが統一されていること

---

## 出力フォーマット（必ずこの構造で出力する）

コードが提示された場合は **修正コードスニペットを各フレームワーク（RN/SwiftUI/Compose）に合わせて提示する**こと。

```
## Mobile Auth Screen Review

### 必須修正
- **[問題の核心]**: [コードから読み取った現在値] → [推奨値と理由]
  ```[言語]
  // 修正前
  // 修正後
  ```

### 推奨改善
- **[項目]**: [現状] → [修正案]

### 実装時対応
- [項目]: [説明]

### 欠落している要素
- [本来あるべきだが実装されていない要素と最適な追加方法]
```

---

## 優先度ガイド

| 優先度 | 項目 |
|--------|------|
| **必須** | A-1, A-7, C-4, C-7, D-1(高さ差8px以上), E-1, F-1(欠如チェック), G-6, I-2 |
| **推奨** | A-5, B-3, C-10, C-11, D-3, D-4, E-5, F-4, G-1, G-2, H-2 |
| **実装時** | A-3, A-4, I-4, I-5, I-6, I-7, J-3, J-6 |
| **検討** | B-1, B-4, E-4, E-6, J-1, J-2 |
