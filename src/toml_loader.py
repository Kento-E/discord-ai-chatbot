#!/usr/bin/env python3
"""
TOMLファイル読み込みモジュール

Python 3.11+ 標準ライブラリの tomllib を使用します。
Python 3.10 以前では tomli パッケージへのフォールバックを提供します。
"""

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Python 3.11未満では tomli パッケージが必要です。\n"
            "pip install tomli を実行してください。"
        ) from exc

__all__ = ["tomllib"]
