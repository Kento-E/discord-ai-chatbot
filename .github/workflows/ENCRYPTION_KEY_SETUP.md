# 暗号鍵の生成手順

このドキュメントでは、知識データを暗号化して保存するための暗号鍵（ENCRYPTION_KEY）の生成方法を説明します。

## 前提条件

- OpenSSL がインストールされている環境（Linux、macOS、Windows WSLなど）

## 暗号鍵の生成方法

### OpenSSL

```bash
openssl rand -base64 32
```

**出力例**:

```
a8B7cD9eF2gH4iJ6kL8mN0pQ1rS3tU5vW7xY9zA1bC3=
```

## GitHub Secretsへの登録手順

生成した暗号鍵をGitHub Secretsに登録します。

1. GitHubリポジトリのページを開く
2. 「Settings」タブをクリック
3. 左サイドバーの「Secrets and variables」→「Actions」をクリック
4. 「New repository secret」ボタンをクリック
5. 以下を入力：
   - **Name**: `ENCRYPTION_KEY`
   - **Secret**: 生成した暗号鍵の値を貼り付け
6. 「Add secret」ボタンをクリック

## セキュリティに関する重要な注意事項

### 暗号鍵の保管

- ✅ **必ずバックアップを取る**: 鍵を紛失すると暗号化データの復号が不可能になります
- ✅ **安全な場所に保管**: パスワードマネージャーや暗号化されたストレージを使用
- ❌ **平文で保存しない**: テキストファイルやメモ帳に保存しない
- ❌ **コミットしない**: Gitリポジトリにコミットしない

### コマンド履歴の削除

暗号鍵を生成したコマンドは、シェルの履歴に残る可能性があります。生成後は履歴を削除することを推奨します。

```bash
# 直前のコマンドを履歴から削除
history -d -1

# または、履歴を完全にクリア（注意: すべての履歴が削除されます）
history -c
```

### 暗号鍵のローテーション

定期的な鍵の更新を推奨します：

- **推奨頻度**: 3〜6ヶ月ごと、または知識データ全体を再生成するタイミング
- **手順**:
  1. 新しい鍵を生成
  2. GitHub Secretsの`ENCRYPTION_KEY`を更新
  3. 「知識データの生成と保存」ワークフローを実行して新しい鍵で暗号化

## 暗号化の仕組み

使用している暗号化方式：

- **アルゴリズム**: AES-256-CBC
- **鍵導出**: PBKDF2（パスワードベース鍵導出関数）
- **ソルト**: OpenSSLにより自動生成

この方式により、暗号鍵なしでの解読は事実上不可能です。

## トラブルシューティング

### 暗号鍵を紛失した場合

暗号鍵を紛失すると、既存の暗号化データは復号できなくなります。

**対処方法**:

1. 新しい暗号鍵を生成
2. GitHub Secretsを更新
3. 「知識データの生成と保存」ワークフローを実行して、新しいデータを生成

### 復号化エラーが発生する場合

**エラーメッセージ例**: `bad decrypt` または `wrong final block length`

**原因**:

- 暗号鍵が間違っている
- 暗号化データが破損している

**対処方法**:

1. GitHub Secretsの`ENCRYPTION_KEY`が正しいか確認
2. 「知識データの生成と保存」ワークフローを再実行

## 関連ファイル

- ワークフロー: `.github/workflows/generate-knowledge-data.yml`
- ワークフロー: `.github/workflows/run-discord-bot.yml`

## 参考情報

- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AES Encryption](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)
