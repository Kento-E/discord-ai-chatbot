"""
メッセージ分割ユーティリティ

Discordの2000文字制限に対応するため、長いメッセージを複数の部分に分割します。
"""

# Discordの1メッセージあたりの最大文字数
DISCORD_MAX_LENGTH = 2000


def split_message(message, max_length=DISCORD_MAX_LENGTH):
    """
    メッセージを指定された最大長で分割する

    改行位置で優先的に分割し、自然な区切りを保ちます。
    改行がない場合や長すぎる場合は、文字数で強制的に分割します。

    Args:
        message: 分割対象のメッセージ文字列
        max_length: 1つのメッセージの最大文字数（デフォルト: 2000）

    Returns:
        list[str]: 分割されたメッセージのリスト

    Examples:
        >>> split_message("短いメッセージ")
        ['短いメッセージ']

        >>> long_msg = "あ" * 2500
        >>> chunks = split_message(long_msg)
        >>> len(chunks)
        2
        >>> all(len(chunk) <= 2000 for chunk in chunks)
        True
    """
    if not message:
        return []

    # メッセージが最大長以下の場合はそのまま返す
    if len(message) <= max_length:
        return [message]

    chunks = []
    remaining = message

    while remaining:
        # 残りが最大長以下なら追加して終了
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # 最大長以内で改行位置を探す
        split_pos = max_length
        chunk = remaining[:max_length]

        # 改行位置で分割を試みる
        last_newline = chunk.rfind("\n")
        if last_newline > 0:  # 0より大きい位置で改行が見つかった場合
            split_pos = last_newline + 1  # 改行文字を含める
        else:
            # 改行がない場合、句点で分割を試みる
            last_period = max(chunk.rfind("。"), chunk.rfind("！"), chunk.rfind("？"))
            if last_period > 0:
                split_pos = last_period + 1  # 句点を含める
            # それでも見つからない場合は、最大長で強制分割

        # チャンクを追加
        chunks.append(remaining[:split_pos])
        remaining = remaining[split_pos:]

    return chunks
