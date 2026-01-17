# Dependabot問題の調査と解決

## 問題の概要

このリポジトリではDependabotによるPR起票が行われていませんでした。一方、同じ所有者の[stock-reportリポジトリ](https://github.com/Kento-E/stock-report)では正常にDependabotが動作し、毎週PRが起票されています。

## 原因の特定

2つのリポジトリの`.github/dependabot.yml`を比較した結果、以下の差分が見つかりました：

### discord-ai-chatbot（本リポジトリ - 動作していない）

```yaml
- package-ecosystem: "pip"
  # ... 他の設定 ...
  rebase-strategy: "auto"  # ← この設定が原因
```

### stock-report（正常に動作）

```yaml
- package-ecosystem: "pip"
  # ... 他の設定 ...
  # rebase-strategy の設定なし
```

## 問題の詳細

`rebase-strategy: "auto"`オプションは、GitHubのDependabotで既知の問題を引き起こすことがあります：

1. **PRが作成されない**: Dependabotが更新をスキャンするものの、PRを作成しない
2. **リベース処理の停止**: Dependabotが「is rebasing this PR」と表示したまま処理が進まない
3. **30日間の非アクティブ後の停止**: 自動リベースが停止する

これらの問題は、GitHubコミュニティやDependabotのissueトラッカーで多数報告されています。

参考：
- [Dependabot rebase-strategy auto issues](https://github.com/dependabot/dependabot-core/issues/13133)
- [Will dependabot rebase all PRs on schedule](https://github.com/orgs/community/discussions/12994)

## 解決方法

`rebase-strategy: "auto"`を削除し、stock-reportと同じ設定に変更しました。

### 変更内容

```diff
- rebase-strategy: "auto"
```

この変更により：
- Dependabotはデフォルトの動作を使用します
- stock-reportと同じ設定になり、同様に動作するはずです
- 不要なリベース処理が発生せず、PRが正常に作成されるようになります

## 推奨される代替案

`rebase-strategy`を使用する必要がある場合は、以下のいずれかを選択してください：

- **設定なし（デフォルト）**: 推奨。ほとんどの場合これで十分です
- `rebase-strategy: "disabled"`: リベースを完全に無効化
- ~~`rebase-strategy: "auto"`~~: 既知の問題があるため非推奨

## 動作確認

修正後、次回の定期実行（毎週土曜日 09:00 JST）でDependabotが正常にPRを作成することを確認してください。

手動でDependabotをトリガーする場合：
1. リポジトリの「Insights」→「Dependency graph」→「Dependabot」に移動
2. 「Recent update jobs」セクションで「Check for updates」をクリック

## 関連ファイル

- `.github/dependabot.yml`: Dependabot設定ファイル
- `.github/workflows/dependabot-auto-approve.yml`: Dependabot PRの自動承認ワークフロー
- `.github/workflows/auto-merge.yml`: PR承認後の自動マージワークフロー
