# 修正プラン: hifi-design-quality 取り込み + 構造改修 + プロジェクトスキル作成

## 背景

hifi-design-quality スキルをマーケットプレイスに追加する過程で、公式仕様との乖離が判明。
改修を実施したが、plugin-structure-guide の配置を誤り（配布用 skills/ に置いてしまった）、
またスキルの品質も skill-creator の基準を満たしていない。

本プランは Phase 1〜6 の各作業を列挙し、完了・未完了・要修正を明確にする。

---

## Phase 1: hifi-design-quality スキルの取り込み [完了・検証済み]

**DoD**: hifi-design-quality が配布用スキルとして正しく登録され、公式フロントマター形式を満たしている。

| 作業 | 状態 | 検証条件 | 検証コマンド/方法 |
|---|---|---|---|
| .skill アーカイブを展開 | 完了 | `skills/hifi-design-quality/SKILL.md` が存在する | `test -f skills/hifi-design-quality/SKILL.md` |
| SKILL.md のフロントマターに name と description がある | 完了 | YAML フロントマターに `name:` と `description:` の2フィールドが存在 | `python3 -c "import yaml; d=yaml.safe_load(open('skills/hifi-design-quality/SKILL.md').read().split('---')[1]); assert 'name' in d and 'description' in d"` |
| plugin.json の skills 配列に追加 | 完了 | `"./skills/hifi-design-quality"` が skills 配列に含まれる | `python3 -c "import json; assert './skills/hifi-design-quality' in json.load(open('.claude-plugin/plugin.json'))['skills']"` |

---

## Phase 2: 公式仕様に基づく構造レビュー [完了]

**DoD**: 公式ドキュメント3ページと Anthropic 公式リポを参照し、plugin.json / marketplace.json / SKILL.md の構造差異を特定・報告済み。成果物: 会話履歴内のレビュー結果5件（(1)version二重定義 (2)keywords不整合 (3)tags未追加 (4)skillsパス形式 (5)description不整合）。

| 作業 | 状態 | 検証条件 | 検証方法 |
|---|---|---|---|
| code.claude.com/docs/en/plugins を取得 | 完了 | plugin.json のスキーマ情報を取得した | WebFetch 実行ログで確認 |
| code.claude.com/docs/en/plugin-marketplaces を取得 | 完了 | marketplace.json のスキーマ情報を取得した | WebFetch 実行ログで確認 |
| code.claude.com/docs/en/plugins-reference を取得 | 完了 | マニフェストの必須/任意フィールド一覧を取得した | WebFetch 実行ログで確認 |
| anthropics/skills リポの marketplace.json を取得 | 完了 | skills フィールドのパス形式（`"./skills/<name>"`）を確認した | gh api 実行ログで確認 |
| レビュー結果5件を報告 | 完了 | (1)version二重定義 (2)keywords不整合 (3)tags未追加 (4)skillsパス形式 (5)description不整合 の5件を報告した | 会話履歴で確認 |

---

## Phase 3: レビュー指摘の改修 [完了]

**DoD**: 4件（3-1〜3-4）が修正済み。version 修正は Phase 4-4 に統合。

| # | 作業 | 状態 | 検証条件 | 検証コマンド |
|---|---|---|---|---|
| 3-1 | plugin.json から version 削除 | 完了 | plugin.json に `"version"` キーが存在しない | `python3 -c "import json; assert 'version' not in json.load(open('.claude-plugin/plugin.json'))"` |
| 3-2 | keywords を plugin.json と marketplace.json で統一 | 完了 | 2ファイルの keywords 配列が同一 | `python3 -c "import json; p=json.load(open('.claude-plugin/plugin.json')); m=json.load(open('.claude-plugin/marketplace.json')); assert p['keywords']==m['plugins'][0]['keywords']"` |
| 3-3 | marketplace.json の tags に hifi-design 追加 | 完了 | tags 配列に `"hifi-design"` が含まれる | `python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); assert 'hifi-design' in m['plugins'][0]['tags']"` |
| 3-4 | skills パスを `"./skills/<name>"` 形式に修正 | 完了 | skills 配列の各要素が `"./skills/"` で始まる | `python3 -c "import json; assert all(s.startswith('./skills/') for s in json.load(open('.claude-plugin/plugin.json'))['skills'])"` |

---

## Phase 4: plugin-structure-guide の配布用スキルからの除去 [完了・検証済み]

**DoD**: plugin-structure-guide が配布用コンポーネント（skills/, plugin.json, marketplace.json）から除去され、marketplace.json の version が 1.4.0 に更新されている。

| # | 作業 | 状態 | 検証条件 | 検証コマンド |
|---|---|---|---|---|
| 4-1 | `skills/plugin-structure-guide/` ディレクトリを削除 | 完了 | `skills/plugin-structure-guide/` が存在しない | `test ! -d skills/plugin-structure-guide` |
| 4-2 | plugin.json の skills 配列から `"./skills/plugin-structure-guide"` を除去 | 完了 | skills 配列に `plugin-structure-guide` を含む文字列がない | `python3 -c "import json; assert not any('plugin-structure-guide' in s for s in json.load(open('.claude-plugin/plugin.json'))['skills'])"` |
| 4-3 | marketplace.json の description から "plugin structure guide" を除去 | 完了 | plugins[0].description に "plugin structure guide" が含まれない | `python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); assert 'plugin structure guide' not in m['plugins'][0]['description'].lower()"` |
| 4-4 | marketplace.json の version を 1.4.0 に設定 | 完了 | `metadata.version == "1.4.0"` かつ `plugins[0].version == "1.4.0"` | `python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); assert m['metadata']['version']=='1.4.0'; assert m['plugins'][0]['version']=='1.4.0'"` |

---

## Phase 5: plugin-structure-guide を skill-creator 手順で再作成 [完了・検証済み]

**DoD**: skill-creator の品質基準を満たす SKILL.md が `.claude/skills/plugin-structure-guide/SKILL.md` に配置され、テストプロンプトで動作確認済み。ユーザーが最終承認（対話型スキル作成のため人手判定は不可避）。

### 5A: 設計

| # | 作業 | 状態 | 検証条件 | 検証方法 |
|---|---|---|---|---|
| 5A-1 | 意図の明確化: スキルの目的、トリガー条件、期待出力を定義 | 完了 | 目的・トリガー条件・出力形式の3点が文書化されている | ユーザー確認 |
| 5A-2 | ユーザーインタビュー: エッジケース、成功基準、スコープ | 完了 | ユーザーからの回答を得ている | 会話履歴で確認 |
| 5A-3 | 参照リソースの特定: 公式ドキュメント URL、既存スキルの参考箇所 | 完了 | 参照リソース一覧が文書化されている | ユーザー確認 |

### 5B: 実装

| # | 作業 | 状態 | 検証条件 | 検証方法 |
|---|---|---|---|---|
| 5B-1 | skill-creator の init_skill.py でスキルを初期化 | 完了 | `.claude/skills/plugin-structure-guide/SKILL.md` が存在しフロントマターに name がある | `test -f .claude/skills/plugin-structure-guide/SKILL.md && python3 -c "import yaml; d=yaml.safe_load(open('.claude/skills/plugin-structure-guide/SKILL.md').read().split('---')[1]); assert 'name' in d"` |
| 5B-2 | SKILL.md ドラフト作成（手順・チェックリスト記述） | 完了 | YAML フロントマターに name/description があり、本文に Step 見出し2件以上・チェックリスト3件以上・検証コマンド3件以上 | `python3 -c "import yaml,re; c=open('.claude/skills/plugin-structure-guide/SKILL.md').read(); p=c.split('---'); fm=yaml.safe_load(p[1]); assert 'name' in fm and 'description' in fm; b='---'.join(p[2:]); assert len(re.findall(r'^#{2,3}\s+Step\s+\d',b,re.MULTILINE))>=2; assert len(re.findall(r'^- \[ \]',b,re.MULTILINE))>=3; assert len(re.findall(r'python3 -c\|claude plugin validate\|test -f',b))>=3"` |
| 5B-3 | skill-creator の quick_validate.py で品質基準を検証 | 完了 | quick_validate.py が全項目パス（終了コード 0） | `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .claude/skills/plugin-structure-guide` |

### 5C: テスト

| # | 作業 | 状態 | 検証条件 | 検証方法 |
|---|---|---|---|---|
| 5C-1 | テストプロンプト 2-3 件を作成しユーザーに確認 | 完了 | ユーザーが承認したテストプロンプトが 2 件以上ある | ユーザー確認 |
| 5C-2 | テスト実行: 各プロンプトでスキルを適用し結果を確認 | 完了 | テスト結果をユーザーに提示し、フィードバックを受領 | テスト実行ログ + ユーザーフィードバック |
| 5C-3 | フィードバックに基づく SKILL.md の改善 | 完了 | ユーザーが品質を承認（「OK」または具体的修正なし） | ユーザー確認 |
| 5C-4 | 改善後に quick_validate.py で再検証 | 完了 | quick_validate.py が全項目パス（終了コード 0） | `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .claude/skills/plugin-structure-guide` |

### 5D: 配置

| # | 作業 | 状態 | 検証条件 | 検証方法 |
|---|---|---|---|---|
| 5D-1 | `.claude/skills/plugin-structure-guide/SKILL.md` として配置 | 完了 | ファイルが存在し、フロントマターに name と description がある | `test -f .claude/skills/plugin-structure-guide/SKILL.md && python3 -c "import yaml; d=yaml.safe_load(open('.claude/skills/plugin-structure-guide/SKILL.md').read().split('---')[1]); assert 'name' in d and 'description' in d"` |

---

## Phase 6: 最終検証 [完了・全項目パス]

**DoD**: Phase 1〜5 の成果物が公式仕様に準拠し、配布用/プロジェクトローカルの境界が正しく、バリデーションがパスする。

| # | 検証項目 | 期待値 | コマンド |
|---|---|---|---|
| 6-1 | plugin.json に version キーがない | `'version' not in plugin.json` | `python3 -c "import json; assert 'version' not in json.load(open('.claude-plugin/plugin.json'))"` |
| 6-2 | plugin.json の keywords と marketplace.json plugins[0].keywords が一致 | 配列が同一 | `python3 -c "import json; p=json.load(open('.claude-plugin/plugin.json')); m=json.load(open('.claude-plugin/marketplace.json')); assert p['keywords']==m['plugins'][0]['keywords']"` |
| 6-3 | marketplace.json の metadata.version と plugins[0].version が "1.4.0" | 両方 "1.4.0" | `python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); assert m['metadata']['version']=='1.4.0'==m['plugins'][0]['version']"` |
| 6-4 | plugin.json の skills 配列9件が `"./skills/<name>"` 形式 | 9件、各要素が `./skills/` で開始 | `python3 -c "import json; s=json.load(open('.claude-plugin/plugin.json'))['skills']; assert len(s)==9; assert all(x.startswith('./skills/') for x in s)"` |
| 6-5 | plugin.json の skills に plugin-structure-guide が含まれない | 文字列 "plugin-structure-guide" なし | `python3 -c "import json; assert not any('plugin-structure-guide' in s for s in json.load(open('.claude-plugin/plugin.json'))['skills'])"` |
| 6-6 | marketplace.json の description に "plugin structure guide" がない | 文字列なし | `python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); assert 'plugin structure guide' not in m['plugins'][0]['description'].lower()"` |
| 6-7 | `skills/plugin-structure-guide/` が存在しない | ディレクトリなし | `test ! -d skills/plugin-structure-guide` |
| 6-8 | `.claude/skills/plugin-structure-guide/SKILL.md` が存在する | ファイルあり | `test -f .claude/skills/plugin-structure-guide/SKILL.md` |
| 6-9 | 配布用スキル9件の SKILL.md にフロントマター(name, description)がある | 9件すべてに name と description が存在 | `python3 -c "import yaml, json; skills=json.load(open('.claude-plugin/plugin.json'))['skills']; [yaml.safe_load(open(s.lstrip('./')+'/SKILL.md').read().split('---')[1]) for s in skills]; assert all('name' in yaml.safe_load(open(s.lstrip('./')+'/SKILL.md').read().split('---')[1]) and 'description' in yaml.safe_load(open(s.lstrip('./')+'/SKILL.md').read().split('---')[1]) for s in skills)"` |
| 6-10 | `claude plugin validate .` がエラーなしで終了する | 終了コード 0 | `claude plugin validate .` |
| 6-11 | plugin.json と marketplace.json の JSON 構文が有効 | パースエラーなし | `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json'))"` |
