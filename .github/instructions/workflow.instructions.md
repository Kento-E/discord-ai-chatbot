# Copilot・自動生成ツール向け GitHub Actions ワークフロー指示

GitHub Actionsワークフローを作成・編集する際は、以下のルールを厳守してください。

## 環境変数の一貫性

### 必須チェック項目

- **ワークフロー内の全ステップで必要な環境変数を設定すること**
  - あるステップで使用している環境変数は、それを必要とする他のすべてのステップでも設定する
  - 特にSecretsを参照する環境変数は漏れがないか注意深く確認する

- **ドキュメント（README.md）と実際のワークフローファイルの整合性を保つ**
  - ワークフローの「必要な環境変数」セクションに記載されている変数は、すべて実際のワークフローファイルで設定されていることを確認
  - ワークフローファイルで使用している環境変数は、すべてドキュメントに記載されていることを確認

### 環境変数設定のベストプラクティス

- **環境変数は必要なステップすべてに明示的に設定する**
  - グローバルに設定するのではなく、各ステップで明示的に設定することを推奨
  - これにより、どのステップがどの環境変数を使用しているかが明確になる

- **環境変数の設定漏れを防ぐチェックリスト**
  1. ワークフロー内で使用される環境変数をすべてリストアップ
  2. 各ステップで必要な環境変数を特定
  3. 各ステップの`env:`セクションに必要な環境変数がすべて設定されているか確認
  4. ドキュメント（.github/workflows/README.md）の「必要な環境変数」セクションを更新

### よくある間違い

- ❌ **悪い例**: あるステップでは設定されているが、同じ環境変数を必要とする別のステップでは設定されていない

```yaml
- name: Gemini APIモデルの有効性を確認
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}  # ここでは設定されている
  run: python src/validate_gemini_model.py

- name: Discord Botを起動
  env:
    DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
    # GEMINI_API_KEY が設定されていない！
  run: python src/main.py
```

- ✅ **良い例**: 必要な環境変数がすべてのステップで設定されている

```yaml
- name: Gemini APIモデルの有効性を確認
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: python src/validate_gemini_model.py

- name: Discord Botを起動
  env:
    DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
    TARGET_GUILD_ID: ${{ secrets.TARGET_GUILD_ID }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}  # 設定されている
  run: python src/main.py
```

## ワークフロー作成時のチェックリスト

新しいワークフローを作成する際は、以下を確認してください：

- [ ] 各ステップで必要な環境変数がすべて`env:`セクションに設定されているか
- [ ] Secretsを参照する環境変数に設定漏れがないか
- [ ] `.github/workflows/README.md`の「必要な環境変数」セクションが更新されているか
- [ ] 同じ環境変数を使用する他のワークフローとの整合性が取れているか

## ワークフロー更新時のチェックリスト

既存のワークフローを更新する際は、以下を確認してください：

- [ ] 新しいステップを追加した場合、必要な環境変数がすべて設定されているか
- [ ] 環境変数を追加・削除した場合、`.github/workflows/README.md`が更新されているか
- [ ] 他のワークフローで同じパターンの変更が必要でないか確認

---

このファイルは Copilot および自動生成ツール向けの GitHub Actions ワークフロー指示です。
