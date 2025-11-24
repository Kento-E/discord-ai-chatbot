# LLM API統合ガイド

このドキュメントでは、Google Gemini APIを使用した高度な応答生成機能の設定方法を説明します。

## 概要

LLM API統合により、過去のDiscordメッセージを文脈として活用しながら、より自然で創造的な応答を生成できます。

## メリット

- **自然な会話**: 過去メッセージの内容を理解し、文脈に沿った応答を生成
- **柔軟な応答**: 質問に対して、過去のメッセージを組み合わせた詳細な回答が可能
- **無料で利用可能**: Google Gemini 1.5 Flashの無料枠で十分に利用可能

## APIキーの取得

1. [Google AI Studio](https://aistudio.google.com/)にアクセス
2. Googleアカウントでログイン
3. 「Get API Key」をクリック
4. 新しいAPIキーを作成
5. APIキーをコピー（重要: 他の人と共有しないでください）

## 設定方法

### ローカル環境

```bash
export GEMINI_API_KEY="your_api_key_here"
```

または、`.bashrc`や`.zshrc`に追加：

```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### GitHub Actions

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 「New repository secret」をクリック
3. Name: `GEMINI_API_KEY`
4. Value: 取得したAPIキーを貼り付け
5. 「Add secret」をクリック

## 動作確認

### 方法1: Pythonで直接テスト

```bash
export GEMINI_API_KEY="your_api_key_here"
python src/test_llm_integration.py
```

成功すると、以下のような出力が表示されます：

```
✓ GEMINI_API_KEY が設定されています
✓ LLM APIからの応答を取得しました
```

### 方法2: Botで確認

1. Botを起動：

```bash
export DISCORD_TOKEN="your_bot_token"
export TARGET_GUILD_ID="your_guild_id"
export GEMINI_API_KEY="your_api_key"
python src/main.py
```

2. Discordで質問してみる：

```
!ask Pythonでファイルを読み込む方法を教えてください
```

LLM APIを使用している場合、より詳細で自然な応答が返されます。

## フォールバック機能

`GEMINI_API_KEY`が設定されていない場合、または APIエラーが発生した場合、自動的に従来のロジック（Sentence Transformersベース）で動作します。

これにより、APIキーなしでもBotは正常に動作し続けます。

## 料金について

Google Gemini 1.5 Flashは無料枠が提供されています：

- **無料枠**: 1分あたり15リクエスト、1日あたり1,500リクエスト
- **詳細**: [Gemini API Pricing](https://ai.google.dev/pricing)

通常のDiscord Bot使用では、無料枠で十分に利用可能です。

## トラブルシューティング

### APIキーが設定されているか確認

```bash
echo $GEMINI_API_KEY
```

### APIエラーが発生する場合

1. APIキーが正しいか確認
2. インターネット接続を確認
3. [Google AI Studio](https://aistudio.google.com/)でAPIキーが有効か確認
4. 無料枠の制限に達していないか確認

### フォールバックが動作しているか確認

LLM APIが使用できない場合、Botは自動的に従来のロジックで動作します。
エラーメッセージが表示されていないか、ログを確認してください。

## セキュリティ上の注意

- **APIキーは秘密情報です**: Gitにコミットしないでください
- **環境変数で管理**: コードに直接記述しないでください
- **定期的に更新**: 漏洩の可能性がある場合は、新しいキーを生成してください

## 参考リンク

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Gemini API Pricing](https://ai.google.dev/pricing)
