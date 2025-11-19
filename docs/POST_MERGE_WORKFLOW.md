# PRマージ後のワークフロー

## 概要

このドキュメントでは、PRがマージされた後のフォローアップタスクの処理方法について説明します。

## 重要な制約事項

**GitHubの自動化ワークフローでは、PRマージ後に新しいPRを自動で作成することはできません。**

- 現在のGitHub Actionsワークフローは、PRの自動マージやブランチ削除などの自動化を提供していますが、マージ後に新しいIssueやPRを自動作成する機能は含まれていません
- フォローアップタスク（新機能の追加、リファクタリング、リンターツールの導入など）に取り組む場合は、手動でIssueとPRを作成する必要があります

## PRマージ後の手動ワークフロー

### 1. フォローアップタスクの特定

PRのレビューコメントやディスカッションから、次に取り組むべきタスクを特定します。

**フォローアップタスクの例:**

- コードの改善やリファクタリング
- リンターツールやフォーマッターの導入
- テストカバレッジの向上
- ドキュメントの追加や更新
- Issueテンプレートの追加や改善
- 新機能の実装

### 2. 新しいIssueの作成

1. GitHubリポジトリの「Issues」タブを開く
2. 「New issue」ボタンをクリック
3. 適切なIssueテンプレートを選択（Feature Request、Bug Report、Generalなど）
4. Issueのタイトルと説明を記入
   - タイトル: タスクの概要を簡潔に記述
   - 説明: タスクの詳細、背景、期待される成果を記述
   - 必要に応じて、元のPRやレビューコメントへのリンクを含める
5. ラベル、マイルストーン、担当者などを設定（任意）
6. 「Submit new issue」をクリック

**Issueテンプレートの種類:**

- `.github/ISSUE_TEMPLATE/feature_request.yml`: 新機能のリクエスト
- `.github/ISSUE_TEMPLATE/bug_report.yml`: バグ報告
- `.github/ISSUE_TEMPLATE/general.yml`: 一般的なタスク
- `.github/ISSUE_TEMPLATE/question.yml`: 質問や相談

### 3. 新しいブランチの作成

作成したIssueに対応するブランチを作成します。

```bash
# リポジトリをクローン（まだの場合）
git clone https://github.com/Kento-E/discord-ai-agent.git
cd discord-ai-agent

# 最新のmainブランチを取得
git checkout main
git pull origin main

# 新しいブランチを作成（Issue番号を含めると良い）
git checkout -b feature/issue-XXX-description
# 例: git checkout -b feature/issue-45-add-linter
```

**ブランチ命名規則:**

- `feature/issue-XXX-description`: 新機能や改善
- `fix/issue-XXX-description`: バグ修正
- `docs/issue-XXX-description`: ドキュメント更新
- `refactor/issue-XXX-description`: リファクタリング

### 4. 変更の実装

ブランチ上で必要な変更を実装します。

```bash
# ファイルを編集
# ...

# 変更をステージング
git add .

# コミット（日本語でコミットメッセージを記述）
git commit -m "リンターツールを導入 (#XXX)"

# リモートにプッシュ
git push origin feature/issue-XXX-description
```

### 5. Pull Requestの作成

1. GitHubリポジトリを開く
2. 「Pull requests」タブを開く
3. 「New pull request」ボタンをクリック
4. base: `main`、compare: `feature/issue-XXX-description` を選択
5. 「Create pull request」をクリック
6. PRテンプレートに従って情報を記入
   - タイトル: 変更内容を簡潔に記述（日本語）
   - 説明: 変更の詳細、関連するIssue番号（`Closes #XXX`など）
7. レビュアーを指定（任意）
8. 「Create pull request」をクリック

**PRテンプレート:**

`.github/pull_request_template.md` に定義されているテンプレートに従って記入してください。

### 6. レビューとマージ

1. レビュアーからのフィードバックに対応
2. 必要に応じて追加のコミットをプッシュ
3. レビューが承認されると、自動マージワークフローが動作します
   - `.github/workflows/auto-merge.yml` が自動的にPRをマージ
   - `.github/workflows/auto-delete-branch.yml` がブランチを削除
4. マージ後、関連するIssueが自動的にクローズされます（`Closes #XXX`を記述した場合）

## GitHub Copilot Workspace の利用

GitHub Copilot Workspace を使用している場合、以下の手順でフォローアップタスクに取り組むことができます:

1. **Issueの作成**: 上記の手順に従って手動でIssueを作成
2. **Copilotへの指示**: 作成したIssueをCopilot Workspaceで開き、タスクの詳細を指示
3. **変更の実装**: Copilotが提案する変更を確認・承認
4. **PRの作成**: Copilotが自動的にPRを作成（または手動で作成）

## よくある質問

### Q: PRマージ後に自動でIssueを作成できないのはなぜですか？

A: 現在のGitHub Actionsの制約と、プロジェクトの自動化ポリシーにより、PRマージ後の自動Issue作成は実装されていません。これは以下の理由によります:

- フォローアップタスクは文脈依存であり、自動化が困難
- 不要なIssueの自動作成を避けるため
- 明確な意図を持ってタスクを作成することの重要性

### Q: 複数のフォローアップタスクがある場合はどうすればよいですか？

A: 各タスクに対して個別のIssueを作成することを推奨します。これにより:

- タスクごとに進捗を追跡できる
- 並行して作業できる
- レビューが容易になる

### Q: フォローアップタスクの優先順位はどのように決めればよいですか？

A: 以下の基準を考慮してください:

1. セキュリティに関わる修正は最優先
2. バグ修正
3. ユーザーへの影響が大きい機能改善
4. コード品質の向上（リンター導入など）
5. ドキュメントの改善

## 参考リンク

- [GitHub Actions ワークフロー](.github/workflows/README.md)
- [自動マージワークフロー](.github/workflows/auto-merge.yml)
- [Issueテンプレート](.github/ISSUE_TEMPLATE/)
- [PRテンプレート](.github/pull_request_template.md)

## まとめ

- **PRマージ後の新しいPRの自動作成は不可能**
- フォローアップタスクは手動でIssueを作成し、ブランチとPRを作成する必要がある
- 明確な手順に従うことで、効率的にタスクを管理できる
- 自動マージなどの既存の自動化機能は引き続き利用可能
