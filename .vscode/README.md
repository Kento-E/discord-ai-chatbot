# VS Code 設定ディレクトリ

## このドキュメントの目的

このドキュメントは、VS Code固有の設定ファイル（`.vscode/`ディレクトリ内）の詳細な説明を提供します。

- **対象読者**: 開発環境のセットアップを行う開発者
- **内容**: 設定ファイルの詳細、セットアップ手順、前提条件、トラブルシューティング
- **関連ドキュメント**: プロジェクト全体の概要は [README.md](../README.md) を参照

## 設定ファイル一覧

このディレクトリには、以下のVS Code設定ファイルが含まれています：

- `mcp.json`: MCP (Model Context Protocol) サーバー設定
- `extensions.json`: 推奨VS Code拡張機能

## extensions.json

**推奨VS Code拡張機能設定ファイル**

このファイルは、リポジトリを開いたときにVS Codeが自動的にインストールを推奨する拡張機能を定義しています。

### 推奨拡張機能

- `github.copilot`: GitHub Copilot拡張機能（MCP機能を利用するために必要）

## mcp.json

**MCPサーバー設定ファイル**

このファイルは、GitHub CopilotがMCPを通じてリポジトリ情報にアクセスするための設定を定義しています。

### 機能

このファイルでは、以下のMCPサーバーを設定しています：

#### 1. GitHub MCP Server

- DockerコンテナでGitHub MCP Serverを起動
- GitHub Copilotにリポジトリの詳細情報を提供（Issue、Pull Request、コミット履歴など）
- Personal Access Tokenをプロンプト入力方式で取得し、リポジトリにコミットしない安全な設計

**参考**: [GitHub公式: Setting up the GitHub MCP Server](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server)

#### 2. Filesystem MCP Server

- ワークスペース内のファイルシステムへの安全なアクセスを提供
- 設定ファイル（config.json、YAMLなど）の編集支援
- ファイル検索・一括編集機能

#### 3. Python Analyzer MCP Server

- Ruffによるコード品質チェック
- 未使用コードの検出（Vulture統合）
- pytest統合によるテストサポート
- Pythonプロジェクトのコード品質維持に最適

### 使用方法

1. **前提条件**
   - VS Code（最新版推奨）
   - GitHub Copilot拡張機能がインストールされていること
   - Dockerがインストールされていること（GitHub MCP Server用）
   - Node.js/npxがインストールされていること（Filesystem MCP Server用）
   - uvx（Python用パッケージランナー）がインストールされていること（Python Analyzer用）

     ```bash
     pip install uv
     ```

     **注**: `uv`パッケージをインストールすると、`uvx`コマンドも同時にインストールされます。

2. **初回起動時の設定**
   - VS Codeでこのリポジトリを開くと、GitHub Personal Access Tokenの入力を求められます
   - トークンの取得方法は、このドキュメントの「セキュリティ」セクションを参照してください

3. **MCPサーバーの起動**
   - VS Codeが自動的に各MCPサーバーを起動します：
     - **GitHub**: Dockerコンテナで起動
     - **Filesystem**: npx経由で起動（Node.jsパッケージ）
     - **Python Analyzer**: uvx経由で起動（Pythonパッケージ）
   - GitHub Copilotがリポジトリ情報、ファイルシステム、コード分析ツールにアクセス可能になります

### セキュリティ

#### Personal Access Tokenの生成

1. [GitHub Settings](https://github.com/settings/tokens) でトークンを生成
2. 必要な権限スコープ:
   - `repo`: リポジトリへのアクセス（必須）
   - `read:org`: 組織情報の読み取り（推奨）
   - `read:user`: ユーザー情報の読み取り（推奨）
   - `workflow`: GitHub Actionsワークフローへのアクセス（オプション - ワークフロー情報が必要な場合のみ）

#### 注意事項

- **Personal Access Tokenは絶対にコミットしないでください**
- このファイル（mcp.json）は安全にリポジトリ管理できます（トークンは含まれていません）
- 使用しなくなったトークンは、GitHubの設定画面から必ず削除してください

### トラブルシューティング

#### Dockerが起動しない

- Dockerがインストールされているか確認してください
- Dockerデーモンが起動しているか確認してください

#### Node.js/npxがインストールされていない

- Filesystem MCP Serverを使用するにはNode.jsが必要です
- [Node.js公式サイト](https://nodejs.org/)からインストールしてください

#### uvxがインストールされていない

- Python Analyzer MCP Serverを使用するにはuvxが必要です
- 以下のコマンドでインストールできます：

  ```bash
  pip install uv
  ```

#### トークン入力のプロンプトが表示されない

- VS Codeを再起動してください
- GitHub Copilot拡張機能が最新版か確認してください

#### MCP Serverに接続できない

- GitHub Personal Access Tokenの権限スコープを確認してください（詳細は [セキュリティ](#セキュリティ) セクションを参照）
- トークンの有効期限が切れていないか確認してください
- 各MCPサーバーの前提条件（Docker、Node.js、uvx）が満たされているか確認してください

### 参考リンク

- [VS Code: Use MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [リポジトリのREADME - MCP サポートセクション](../README.md#mcp-model-context-protocol-サポート)
