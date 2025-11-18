# 知識データのRelease自動アップロード機能

## 概要

このドキュメントでは、知識データをGitHub Releaseに自動的にアップロードし、永続的に保存する仕組みについて説明します。

## アーキテクチャ

### フローダイアグラム

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 知識データの生成と保存ワークフロー                                 │
│    (generate-knowledge-data.yml)                                    │
├─────────────────────────────────────────────────────────────────────┤
│ • Discordからメッセージ取得                                          │
│ • 埋め込みデータ生成                                                 │
│ • AES-256-CBCで暗号化                                                │
│ • アーティファクトとして保存 (knowledge-data-encrypted)               │
└────────────────────┬────────────────────────────────────────────────┘
                     │ 成功時にトリガー
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. 知識データのRelease自動アップロードワークフロー                    │
│    (upload-knowledge-to-release.yml)                                │
├─────────────────────────────────────────────────────────────────────┤
│ • アーティファクトをダウンロード                                      │
│ • タイムスタンプベースのタグを生成                                    │
│   例: knowledge-data-20241117-105300                                │
│ • GitHub Releaseを作成                                               │
│ • 暗号化データをRelease assetとしてアップロード                       │
│ • 古いRelease（6件目以降）を自動削除                                  │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ GitHub Release│
              │               │
              │ 最新5件保持   │
              └──────┬────────┘
                     │
                     │ 最新版をダウンロード
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Discord Botの実行ワークフロー                                     │
│    (run-discord-bot.yml)                                            │
├─────────────────────────────────────────────────────────────────────┤
│ • 最新のknowledge-data-* Releaseを検索                               │
│ • Release assetをダウンロード                                        │
│ • 暗号化データを復号化                                                │
│ • Discord Botを起動                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 利点

### 1. 永続的な保存

- **GitHub Actionsのアーティファクト保持期間（90日）に依存しない**
- Releaseは削除されない限り永続的に保持される
- 最新5件のみ保持することでストレージを節約

### 2. アクセス性の向上

- public リポジトリでは誰でもダウンロード可能
- GitHub UIから直接ダウンロードできる
- GitHub APIを使用したプログラマティックなアクセスが可能

### 3. バージョン管理

- タイムスタンプ付きタグで履歴が明確
- 特定のバージョンに簡単にロールバック可能
- Release notesで生成時の情報を確認可能

### 4. 自動化

- ワークフローが完全自動化
- 手動操作不要
- エラー時の詳細なログ出力

## 技術詳細

### タグ命名規則

```
knowledge-data-YYYYMMDD-HHMMSS-{workflow_run_id}
```

例:
- `knowledge-data-20241117-105300-12345678` → 2024年11月17日 10:53:00 UTC、ワークフロー実行ID: 12345678

### Release保持ポリシー

- **最新5件のみ保持**
- 6件目以降は自動削除
- 削除時にタグも同時に削除（`--cleanup-tag`）

### 暗号化方式

暗号化の詳細については [ENCRYPTION_KEY_SETUP.md](../.github/workflows/ENCRYPTION_KEY_SETUP.md) を参照してください。

- **アルゴリズム**: AES-256-CBC
- **鍵導出**: PBKDF2

### 必要な権限

#### upload-knowledge-to-release.yml

```yaml
permissions:
  contents: write  # Release作成とタグ操作
```

#### run-discord-bot.yml

```yaml
permissions:
  contents: read  # Releaseの読み取り
```

## 使用方法

### 1. 初回セットアップ

1. GitHub Secretsを設定（詳細: [ENCRYPTION_KEY_SETUP.md](../.github/workflows/ENCRYPTION_KEY_SETUP.md)）：
   - `DISCORD_TOKEN`: Discord Botのトークン
   - `TARGET_GUILD_ID`: 取得対象のサーバーID
   - `ENCRYPTION_KEY`: 暗号化/復号化用の鍵

2. 「知識データの生成と保存」ワークフローを実行

3. 完了後、自動的にReleaseが作成される

### 2. Botの起動

1. 「Discord Botの実行」ワークフローを実行
2. 最新のReleaseから知識データが自動ダウンロードされる
3. Botが起動する

### 3. 知識データの更新

1. 「知識データの生成と保存」ワークフローを再実行
2. 新しいReleaseが自動作成される
3. 次回のBot起動時に最新版が使用される

## トラブルシューティング

### Releaseが作成されない

**原因**:
- 元のワークフロー（知識データの生成と保存）が失敗している
- アーティファクトが正しく保存されていない

**対処方法**:
1. 「知識データの生成と保存」ワークフローのログを確認
2. 必要なSecrets（DISCORD_TOKEN、TARGET_GUILD_ID、ENCRYPTION_KEY）が設定されているか確認
3. ワークフローを再実行

### Botが「知識データが見つかりません」エラーを出す

**原因**:
- knowledge-data-* タグのReleaseが存在しない

**対処方法**:
1. Releasesページを確認
2. 「知識データの生成と保存」ワークフローを実行
3. Release作成の完了を確認後、Botワークフローを再実行

### 復号化エラーが発生する

詳細なトラブルシューティングは [ENCRYPTION_KEY_SETUP.md](../.github/workflows/ENCRYPTION_KEY_SETUP.md) を参照してください。

**原因**:
- ENCRYPTION_KEYが間違っている
- 生成時と実行時で異なる鍵を使用している

## セキュリティ考慮事項

暗号鍵の管理とセキュリティの詳細については [ENCRYPTION_KEY_SETUP.md](../.github/workflows/ENCRYPTION_KEY_SETUP.md) を参照してください。

### Public リポジトリでの運用

- **暗号化は必須**: 知識データは暗号化されてReleaseに保存される
- **鍵の管理**: ENCRYPTION_KEYは絶対にコミットしない
- **Release内容**: Release notesには機密情報を含めない

## 関連ファイル

- [.github/workflows/upload-knowledge-to-release.yml](../.github/workflows/upload-knowledge-to-release.yml)
- [.github/workflows/run-discord-bot.yml](../.github/workflows/run-discord-bot.yml)
- [.github/workflows/generate-knowledge-data.yml](../.github/workflows/generate-knowledge-data.yml)
- [.github/workflows/ENCRYPTION_KEY_SETUP.md](../.github/workflows/ENCRYPTION_KEY_SETUP.md)
- [.github/workflows/README.md](../.github/workflows/README.md)
