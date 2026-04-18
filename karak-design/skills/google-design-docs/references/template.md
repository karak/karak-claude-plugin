# デザインドキュメント テンプレート

## 目次

1. [テンプレート構造](#テンプレート構造)
2. [各セクションの書き方](#各セクションの書き方)
3. [サンプル: ユーザー認証システム](#サンプル-ユーザー認証システム)

---

## テンプレート構造

```markdown
# [プロジェクト名] Design Doc

**Author**: [著者名]
**Reviewers**: [レビュアー名]
**Status**: Draft | In Review | Approved | Implemented
**Last Updated**: [日付]

## Context and Scope

[背景と範囲を2-3段落で記述]

## Goals and Non-Goals

### Goals
- [目標1]
- [目標2]

### Non-Goals
- [非目標1: なぜ範囲外か]
- [非目標2: なぜ範囲外か]

## The Actual Design

### System Overview

[システム全体像を図で示す]

```
[ASCII図またはMermaid図]
```

### API Design

[主要なAPIエンドポイントやインターフェースの概要]

### Data Model

[データ構造の概要（スキーマ全文は避ける）]

### Key Algorithms

[重要なアルゴリズムがあれば記述]

## Alternatives Considered

### Option A: [選択肢A]
- **Pros**: [利点]
- **Cons**: [欠点]
- **Why not chosen**: [不採用理由]

### Option B: [選択肢B]
- **Pros**: [利点]
- **Cons**: [欠点]
- **Why not chosen**: [不採用理由]

### Chosen Approach: [採用アプローチ]
[なぜこのアプローチを選んだかの理由]

## Cross-cutting Concerns

### Security
[セキュリティ考慮事項]

### Privacy
[プライバシー考慮事項]

### Observability
[監視・ログ・メトリクス]

## Open Questions

- [ ] [未解決の質問1]
- [ ] [未解決の質問2]
```

---

## 各セクションの書き方

### Context and Scope

**目的**: 読者に背景を与え、文書の範囲を明確にする

**書き方**:
- 客観的な事実のみを記述
- 現在のシステムの問題点や制約を説明
- この設計がどの部分に影響するかを明示

**良い例**:
> 現在のログインシステムはパスワード認証のみをサポートしている。
> ユーザー調査によると、60%のユーザーがソーシャルログインを希望している。
> このドキュメントでは、OAuth 2.0を用いたソーシャルログイン機能の設計を扱う。

**悪い例**:
> 私たちは素晴らしい新機能を追加する必要がある。
> これにより顧客は非常に満足するだろう。

### Goals and Non-Goals

**目的**: 成功基準を明確にし、スコープクリープを防ぐ

**Goals の書き方**:
- 測定可能で具体的な目標
- 優先順位を明示（P0/P1/P2など）

**Non-Goals の書き方**:
- 意図的に範囲外とするものとその理由
- 将来的に検討する可能性があるものも記載

**良い例**:
> **Goals**:
> - P0: Google/Facebook OAuth ログインをサポート
> - P1: 既存アカウントとのリンク機能
>
> **Non-Goals**:
> - Apple Sign-In（iOS 14以上が必要で現在のユーザーベースの30%しかカバーしない）
> - パスワードレス認証（別プロジェクトで検討中）

### The Actual Design

**目的**: 概要から詳細へ段階的に展開

**構成**:
1. **System Overview**: 30秒で理解できる全体像
2. **詳細設計**: 必要な深さまで掘り下げ

**図の活用**:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   Gateway   │───▶│  Auth Svc   │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │  User DB    │
                                      └─────────────┘
```

### Alternatives Considered

**目的**: トレードオフを明示し、設計判断の根拠を記録

**各選択肢に含める要素**:
- 概要説明
- Pros（利点）
- Cons（欠点）
- 不採用理由（採用案以外）

**重要**: 単に「検討した」だけでなく、なぜ採用/不採用かを明記

### Cross-cutting Concerns

**目的**: セキュリティ・プライバシー・運用面の検討を確実に行う

**チェックリスト**:
- [ ] 認証・認可は適切か
- [ ] 個人情報の取り扱いは適切か
- [ ] ログに機密情報が含まれないか
- [ ] 障害時の影響範囲は把握しているか
- [ ] ロールバック手順はあるか

---

## サンプル: ユーザー認証システム

```markdown
# OAuth Social Login Design Doc

**Author**: Taro Yamada
**Reviewers**: Hanako Suzuki, Security Team
**Status**: In Review
**Last Updated**: 2025-01-15

## Context and Scope

当社のWebアプリケーションは現在、メールアドレスとパスワードによる
認証のみをサポートしている。2024年Q4のユーザー調査では：

- 65%のユーザーがソーシャルログインを希望
- 新規登録の離脱率が45%（業界平均30%）
- パスワードリセットリクエストが月間1,200件

本ドキュメントでは、Google OAuth 2.0を用いたソーシャルログイン機能の
設計を扱う。Facebook、Apple等の他プロバイダーは将来の拡張として
アーキテクチャで考慮するが、初期実装には含めない。

## Goals and Non-Goals

### Goals
- P0: Google OAuth 2.0 によるログイン/新規登録
- P0: 既存のメール/パスワードアカウントとのリンク
- P1: ログイン成功率を95%以上に維持
- P2: 将来の他プロバイダー追加を容易にする設計

### Non-Goals
- Facebook/Apple/Twitter ログイン（Phase 2で検討）
- パスワードレス認証（別プロジェクト AUTH-2024-Q2）
- 二要素認証の変更（現行のTOTPを維持）
- 企業向けSAML/OIDC対応（エンタープライズチームの担当）

## The Actual Design

### System Overview

```
┌──────────────┐         ┌──────────────┐
│    Browser   │◀───────▶│   Frontend   │
└──────────────┘         └──────────────┘
                                │
                                ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Google     │◀───────▶│  API Gateway │◀───────▶│  Auth Svc    │
│   OAuth      │         └──────────────┘         └──────────────┘
└──────────────┘                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │   User DB    │
                                                  │  (PostgreSQL)│
                                                  └──────────────┘
```

### Authentication Flow

1. ユーザーが「Googleでログイン」ボタンをクリック
2. フロントエンドがGoogle OAuth認可URLにリダイレクト
3. ユーザーがGoogleで認証・認可
4. GoogleがコールバックURLにauthorization codeを返却
5. バックエンドがcodeをaccess tokenに交換
6. Googleのuserinfo APIからメールアドレスを取得
7. 既存ユーザーの照合または新規作成
8. セッション発行

### Data Model

usersテーブルに以下のカラムを追加：

| Column | Type | Description |
|--------|------|-------------|
| google_id | VARCHAR(255) | Google Subject ID |
| auth_provider | ENUM | 'email', 'google', 'linked' |
| linked_at | TIMESTAMP | アカウントリンク日時 |

既存の `email` と `password_hash` は維持し、
`auth_provider='linked'` の場合は両方の認証方法を許可。

### API Design

```
POST /api/v1/auth/google/callback
  Request: { code: string, state: string }
  Response: { access_token: string, user: User }

POST /api/v1/auth/link/google
  Request: { google_code: string }
  Headers: Authorization: Bearer <existing_token>
  Response: { success: boolean }
```

## Alternatives Considered

### Option A: Firebase Authentication

**Pros**:
- 実装が容易（SDK提供）
- 複数プロバイダーを統一的に扱える
- セキュリティアップデートが自動

**Cons**:
- ベンダーロックイン
- ユーザーデータがGoogleに保存される
- 月額コストが発生（MAU 50,000以上で有料）

**不採用理由**: 将来の柔軟性とデータ主権の観点から自社実装を選択

### Option B: Auth0

**Pros**:
- エンタープライズ機能が充実
- コンプライアンス対応が容易

**Cons**:
- 高コスト（月額$2,000以上）
- オーバースペック

**不採用理由**: 現時点でのニーズに対してコストが見合わない

### Chosen Approach: 自社実装 + Google OAuth SDK

**理由**:
- 既存のAuth Serviceを拡張可能
- データを自社DBに保持
- 将来のプロバイダー追加が容易
- 学習コストは許容範囲

## Cross-cutting Concerns

### Security

- CSRF対策: stateパラメータによる検証
- トークン保存: HttpOnly + Secure + SameSite=Strict Cookie
- Google IDは内部IDにマッピング（外部に露出しない）
- rate limiting: 10 req/min per IP for callback endpoint

### Privacy

- 収集データ: メールアドレス、表示名、プロフィール画像URL
- Googleからの追加スコープは要求しない（email, profile のみ）
- プライバシーポリシーの更新が必要

### Observability

- 新規メトリクス: oauth_login_success_total, oauth_login_failure_total
- エラーログ: token exchange失敗時に詳細ログ（トークン値は除く）
- ダッシュボード: Grafanaに認証方法別のログイン数を追加

## Open Questions

- [ ] 既存ユーザーのGoogleアカウントと自動リンクする際の確認フローは？
- [ ] Google側でメールアドレスが変更された場合の扱いは？
- [ ] 実装完了後のパフォーマンステストのスコープは？
```

---

## 良いデザインドキュメントのチェックリスト

- [ ] 30秒で要点が分かるか
- [ ] Goals/Non-Goalsが明確か
- [ ] 図が含まれているか
- [ ] 代替案とトレードオフが記載されているか
- [ ] セキュリティ・プライバシーが検討されているか
- [ ] 未解決の質問がリストされているか
- [ ] 10-20ページ以内に収まっているか
