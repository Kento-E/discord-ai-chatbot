# Copilot・自動生成ツール向け コーディング指示

このプロジェクトでコードを作成・編集する際は、以下のルールを厳守してください。

## エラーハンドリング

### 必須チェック項目

- **リストや配列へのアクセス前に空チェックを実施**
  - `list[0]`のようなアクセスの前に、必ず`if not list:`または`if len(list) > 0:`でチェック
  - 例: `if similar_messages: first_message = similar_messages[0]`

- **`random.choice()`などの関数は空リストでエラーになるため事前チェック必須**
  - 空リストで`random.choice()`を呼ぶとIndexErrorが発生
  - 例: `if endings: ending = random.choice(endings) else: ending = "。"`

- **`dict.get()`でデフォルト値を指定し、Noneチェックを追加**
  - `dict.get(key, default_value)`を使用してNone回避
  - 取得後も値が空でないことを確認
  - 例: `greetings = persona.get('sample_greetings', []); if greetings: ...`

- **ファイル・ディレクトリ操作前に存在確認**
  - ディレクトリ作成: `os.makedirs(path, exist_ok=True)`
  - ファイル存在確認: `if os.path.exists(file_path):`

### 正規表現の結果処理

- **`re.split()`の結果から空文字列を除外**
  - 例: `sentences = [s for s in re.split(r'[。！？]', text) if s.strip()]`
  - 空リスト対策: `response = sentences[0] if sentences else fallback_text`

## コード品質

### リンター実行（必須）

**コード変更後は必ずリンターを実行してコミットすること**

コミット前に以下のいずれかの方法でリンターを実行し、すべてのエラーを修正してください：

#### Copilot向け特別指示

**Copilotがコードを生成する場合、`report_progress`でコミットする前に必ずリンターを実行して修正すること**

**基本方針: 変更したファイルのみをリンターで検証**

```bash
# 変更したファイルのみリンター実行（通常はこれで十分）
# 例: src/ai_chatbot.py を変更した場合
black src/ai_chatbot.py
isort --profile black src/ai_chatbot.py
autoflake --in-place --remove-all-unused-imports --remove-unused-variables src/ai_chatbot.py
flake8 src/ai_chatbot.py

# 複数ファイルを変更した場合
black src/file1.py src/file2.py
isort --profile black src/file1.py src/file2.py
autoflake --in-place --remove-all-unused-imports --remove-unused-variables src/file1.py src/file2.py
flake8 src/file1.py src/file2.py
```

**全ファイルスキャンが必要なケース（例外的）:**
- PR開始時の初回コミット
- CI失敗時に既存エラーの有無を確認する場合

```bash
# 全ファイルスキャン（例外的な場合のみ）
black src/
isort --profile black src/
autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables src/
flake8 src/
```

理由：
- `report_progress`ツールはpre-commitフックをバイパスするため、自動フォーマットが適用されない
- 変更ファイルのみのリンターで効率的にエラーを防止（1-2秒）
- 全ファイルスキャンは不要（CIが実行するため）
- 既存ファイルの既存エラーはCIで検出され、その時点で修正すれば良い

#### 方法1: Pre-commitフック（推奨）

```bash
# 初回のみセットアップ
pre-commit install

# 以降、git commitで自動実行される
git add .
git commit -m "メッセージ"
```

#### 方法2: 手動実行

```bash
# 全リンターをチェックのみ実行（修正なし）
make check

# 全リンターを実行して自動修正
make format

# 個別実行
autoflake --check --recursive --remove-all-unused-imports --remove-unused-variables src/
isort --check-only --profile black src/
black --check src/
flake8 src/
```

#### 方法3: pre-commitコマンド

```bash
# 全ファイルに対して実行
pre-commit run --all-files

# 変更したファイルのみ実行
pre-commit run
```

**重要**: リンターエラーがある状態でコミットしないでください。CI/CDパイプラインで失敗します。

### 基本ルール

- **未使用の変数・importは削除すること**
  - コミット前にリンター（flake8/pylint）を実行して確認
  - IDE/エディタの警告にも注意

- **変数名は明確に**
  - 目的が分かる名前を使用（例: `query_lower`は小文字変換されたクエリと分かる）
  - 略語は慣例的なもののみ使用

- **コメントは必要に応じて追加**
  - 複雑なロジックには説明コメントを追加
  - 自明なコードには不要
  - 既存のコメントスタイルに合わせる
  - **DRY原則に従う**: コメントにコードと同じ情報（変数名、定数値、モデル名など）を記載しない
    - ❌ 悪い例: `# モデルを初期化（gemini-2.0-flashを使用）`
    - ✅ 良い例: `# モデルを初期化`
    - 理由: コードが変更された際にコメントの更新が漏れると、情報が不一致になる

- **削除された機能に関連するコードは完全に削除すること**
  - 参考資料、コメント、使用例なども含めてすべて削除
  - 過去の実装を参考として残さない
  - テストコード内の参考情報表示コードも同様に削除
  
  **ファイル削除時の必須チェックリスト:**
  1. `grep -r "削除対象ファイル名" .` で全参照箇所を検索
  2. README.md、docs/配下、.github/workflows/README.md を確認
  3. コミット前に `git diff` で変更範囲を最終確認
  4. ドキュメント内のリンク・パス参照がすべて削除されているか確認

## テストファイルの管理

- **PR専用テストファイル（プライベート関数のユニットテストなど）は、テスト完了後に同じPR内で削除すること**
  - プライベート関数（`_`で始まる関数）専用のテストファイルは永続化しない
  - 公開APIを通じて機能をテストできる場合、プライベート関数専用のテストファイルは不要
  - 既存のテストファイル（`test_response_logic.py`など）にテストケースを追加する方が保守性が高い
  - 実装検証のために一時的にプライベート関数をテストすることは有用だが、検証完了後は**必ず同じPR内で削除**すること

### テストファイル作成の判断基準

- ✅ **作成してよい一時テストファイル**:
  - プライベート関数の動作検証用
  - 新機能の実装検証用
  - デバッグ・トラブルシューティング用
  - **条件**: テスト完了後、同じPR内で削除すること

- ❌ **永続化すべきでないテストファイル**:
  - テスト内で実装ロジックを複製しているもの
  - 実際のコードをインポートせず、独自実装でテストしているもの
  - プライベート関数のみをテストするもの

- ✅ **永続化すべきテストファイル**:
  - 公開API（`generate_response`、`search_similar_message`など）をテストするもの
  - エンドツーエンドのシナリオテスト
  - 既存テストファイルに統合できないユニークなテストケース

### コード変更時のテスト影響確認

コードやドキュメントを変更した際は、既存テストへの影響を必ず確認すること：

- **参照される文字列を変更した場合**
  - プロンプト設定、ドキュメント、エラーメッセージなど、他のファイルから参照される文字列を変更した際は、その文字列を使用している全テストファイルを確認すること
  - 例: プロンプト内の「AIアドバイザー」を「専門AIアシスタント」に変更した場合、テストコード内で「AIアドバイザー」という文字列を検証している箇所を更新する
  - `grep -r "変更した文字列" src/test_*.py` で影響範囲を確認

- **コード変更後のテスト実行**
  - コード変更後は必ず関連するすべてのテストを実行し、影響を確認すること
  - 変更が完了したと思った時点で、もう一度全テストを実行して最終確認すること
  - テストが失敗した場合は、コード変更による意図的な仕様変更か、バグかを判断し、適切に対応すること

## 推奨ツール

### リンター・フォーマッター

- **flake8**: Pythonコードの静的解析
- **pylint**: より詳細なコード品質チェック
- **autoflake**: 未使用importの自動削除
- **isort**: import文の自動整形
- **black**: コードの自動フォーマット

### 使用方法

```bash
# インストール
pip install flake8 pylint autoflake isort black

# 実行
flake8 src/
pylint src/
autoflake --remove-all-unused-imports --in-place src/*.py
isort src/
black src/
```

## チェックリスト

コード作成・変更時は以下を確認：

- [ ] リスト・配列アクセス前に空チェックを実施したか
- [ ] `random.choice()`等の関数使用前にチェックしたか
- [ ] ファイル・ディレクトリ操作前に存在確認・作成したか
- [ ] 正規表現の結果処理で空文字列を考慮したか
- [ ] 未使用の変数・importを削除したか
- [ ] 変数名は明確か
- [ ] 必要なコメントを追加したか
- [ ] **（Copilot）コミット前にリンター（black, isort, autoflake, flake8）を実行したか**
- [ ] リンターでエラーがないか確認したか
- [ ] 削除した機能に関連するコード（参考資料含む）をすべて削除したか
- [ ] PR専用テストファイルを作成した場合、テスト完了後に同じPR内で削除したか
- [ ] プロンプトやドキュメントなど参照される文字列を変更した場合、その文字列を使用している全テストファイルを確認したか
- [ ] コード変更後に関連するすべてのテストを実行し、影響を確認したか

---

このファイルは Copilot および自動生成ツール向けのコーディング指示です。
