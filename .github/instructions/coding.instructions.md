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
- [ ] リンターでエラーがないか確認したか

---

このファイルは Copilot および自動生成ツール向けのコーディング指示です。
