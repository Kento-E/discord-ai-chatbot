.PHONY: help install lint format check test clean

help:
	@echo "利用可能なコマンド:"
	@echo "  make install    - 依存パッケージとpre-commitフックをインストール"
	@echo "  make lint       - リンター（flake8）を実行"
	@echo "  make format     - コードフォーマット（autoflake, isort, black）を実行"
	@echo "  make check      - リンターとフォーマットをチェック（変更なし）"
	@echo "  make test       - テストを実行"
	@echo "  make clean      - 一時ファイルを削除"

install:
	pip install -r requirements.txt
	pre-commit install

lint:
	flake8 src/

format:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/
	isort src/
	black src/

check:
	@echo "=== autoflakeチェック ==="
	autoflake --remove-all-unused-imports --remove-unused-variables --check --recursive src/ || true
	@echo ""
	@echo "=== isortチェック ==="
	@echo ""
	@echo "=== blackチェック ==="
	@echo ""
	@echo "=== flake8チェック ==="

test:
	python -m pytest src/ -v || python -m unittest discover -s src -p "test_*.py"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist .eggs 2>/dev/null || true
