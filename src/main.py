import os

import discord

EMBED_PATH = os.path.join(os.path.dirname(__file__), "../data/embeddings.json")

# 環境変数から機密情報を読み取る
TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID_STR = os.environ.get("TARGET_GUILD_ID")

if not TOKEN:
    raise ValueError("環境変数 DISCORD_TOKEN が設定されていません")
if not GUILD_ID_STR:
    raise ValueError("環境変数 TARGET_GUILD_ID が設定されていません")

GUILD_ID = int(GUILD_ID_STR)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# ai_agent モジュールのインポート（埋め込みデータが存在する場合のみ）
# 注意: 遅延ロードにより、実際のデータロードは初回応答時に行われます
generate_response = None
if os.path.exists(EMBED_PATH):
    try:
        from ai_agent import generate_response

        print("✅ AIエージェント機能が有効化されました")
        print("   💡 モデルとデータは初回応答時に自動的にロードされます")
    except Exception as e:
        print(f"❌ AIエージェントのロード中にエラーが発生しました: {e}")
        generate_response = None


@client.event
async def on_ready():
    print(f"✅ ログイン成功: {client.user}")
    print("🤖 Botが起動し、メッセージの受信を開始しました")
    if generate_response:
        print("💬 メンションまたは !ask コマンドで質問できます")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Botへのメンション or !ask コマンドで応答
    if client.user in message.mentions or message.content.startswith("!ask "):
        query = (
            message.content.replace("!ask ", "")
            .replace(f"<@{client.user.id}>", "")
            .strip()
        )
        if not query:
            await message.channel.send("質問内容を入力してください。")
            return
        if os.path.exists(EMBED_PATH) and generate_response:
            # 予測返信を生成
            try:
                # 初回初期化の責任をai_agentモジュール側に持たせる
                from ai_agent import ensure_initialized_with_callback

                loading_msg = None

                def on_first_init():
                    """初回初期化開始時のコールバック（処理なし）"""

                # 初期化を実行し、初回かどうかを判定
                was_already_initialized = ensure_initialized_with_callback(
                    on_first_init
                )

                # 初回初期化の場合のみローディングメッセージを表示
                if not was_already_initialized:
                    loading_msg = await message.channel.send(
                        "🔄 初回起動完了！AIモデルとデータをロードしました"
                    )

                try:
                    response = generate_response(query)
                finally:
                    # エラーが発生してもローディングメッセージを削除
                    if loading_msg:
                        await loading_msg.delete()

                await message.channel.send(response)
            except Exception as e:
                await message.channel.send(f"エラーが発生しました: {str(e)}")
        else:
            help_msg = (
                "知識データが未生成です。まずメッセージ取得・整形を行ってください。\n"
                "\n"
                "**手順:**\n"
                "1. `python src/fetch_messages.py` でメッセージ取得\n"
                "2. `python src/prepare_dataset.py` で埋め込みデータ生成\n"
                "3. Botを再起動\n"
                "\n"
                "詳細は docs/USAGE.md またはREADMEをご覧ください。"
            )
            await message.channel.send(help_msg)


if __name__ == "__main__":
    client.run(TOKEN)
