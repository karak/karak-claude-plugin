---
name: plugin-structure-guide
description: karak-claude-plugin のプラグイン構造ガイド。新しいスキルの追加、plugin.json / marketplace.json の修正、マーケットプレイス公開準備時に使用する。公式仕様に基づくチェックリストとバリデーションコマンドを提供する。
---

# Plugin Structure Guide

karak-claude-plugin に新しいスキルを追加する際の構造ルールとチェックリスト。
Phase 2 レビューで発見された5つの不整合（version二重定義、keywords不整合、tags未追加、skillsパス形式、description不整合）を防止する。

## ファイル構成

```
.claude-plugin/
  plugin.json          # プラグインマニフェスト
  marketplace.json     # マーケットプレイス公開メタデータ
skills/
  <skill-name>/
    SKILL.md           # スキル定義（フロントマター必須）
```

## スキル追加ワークフロー

### Step 1: SKILL.md を作成

`skills/<skill-name>/SKILL.md` を作成し、YAML フロントマターに `name` と `description` を記述する。

```yaml
---
name: <skill-name>
description: <スキルの説明。トリガー条件と用途を含める>
---
```

**検証:**
```bash
python3 -c "import yaml; d=yaml.safe_load(open('skills/<skill-name>/SKILL.md').read().split('---')[1]); assert 'name' in d and 'description' in d"
```

### Step 2: plugin.json に登録

`skills` 配列に `"./skills/<skill-name>"` 形式で追加する。

**ルール:**
- パスは必ず `./skills/` で始める（`skills/` ではなく `./skills/`）
- `version` フィールドは plugin.json に含めない（marketplace.json のみ）

**検証:**
```bash
python3 -c "import json; s=json.load(open('.claude-plugin/plugin.json'))['skills']; assert all(x.startswith('./skills/') for x in s)"
python3 -c "import json; assert 'version' not in json.load(open('.claude-plugin/plugin.json'))"
```

### Step 3: marketplace.json を更新

以下の3点を確認・更新する。

#### 3a: description に新スキルを反映

`plugins[0].description` にスキル名を追加する。

#### 3b: keywords を plugin.json と一致させる

```bash
python3 -c "import json; p=json.load(open('.claude-plugin/plugin.json')); m=json.load(open('.claude-plugin/marketplace.json')); assert p['keywords']==m['plugins'][0]['keywords']"
```

#### 3c: tags に関連タグを追加（必要に応じて）

#### 3d: Leave versions unchanged

Don't bump `metadata.version` or any plugin `version` in a work PR. Versions are bumped only in the release-prep PR before a develop→main merge; see CLAUDE.md "Branching and releases".

### Step 4: バリデーション

```bash
# JSON 構文チェック
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json'))"

# フロントマター一括チェック
python3 -c "
import yaml, json
skills = json.load(open('.claude-plugin/plugin.json'))['skills']
for s in skills:
    path = s.lstrip('./') + '/SKILL.md'
    d = yaml.safe_load(open(path).read().split('---')[1])
    assert 'name' in d and 'description' in d, f'{path}: missing name or description'
print('All skills valid')
"

# プラグインバリデータ
claude plugin validate .
```

## チェックリスト

新スキル追加時に以下を確認する：

- [ ] `skills/<name>/SKILL.md` が存在し、フロントマターに `name` と `description` がある
- [ ] plugin.json の `skills` 配列に `"./skills/<name>"` 形式で追加した
- [ ] plugin.json に `version` フィールドがない
- [ ] marketplace.json の `description` に新スキルが含まれている
- [ ] marketplace.json の `keywords` が plugin.json の `keywords` と一致している
- [ ] Versions in marketplace.json are unchanged (they are bumped only at release time)
- [ ] `claude plugin validate .` がエラーなしで通る

## よくあるミス

| ミス | 正しい対応 |
|------|-----------|
| plugin.json に `version` を追加してしまう | marketplace.json のみで version を管理する |
| skills パスを `"skills/<name>"` にしてしまう | `"./skills/<name>"` と先頭に `./` を付ける |
| marketplace.json の keywords を更新し忘れる | plugin.json と marketplace.json で同一配列にする |
| Bumping versions in a work PR | Leave versions alone; bump them in the release-prep PR (CLAUDE.md) |
| プロジェクトローカルスキルを配布用 skills/ に置く | `.claude/skills/` に配置する（配布対象にしない） |
