import os

import discord
from discord import app_commands

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/knowledge.db")

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


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # スラッシュコマンドをギルドに同期
        try:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print("✅ スラッシュコマンドをギルドに同期しました")
        except Exception as e:
            print(f"⚠️ スラッシュコマンドの同期に失敗しました: {e}")


client = MyClient(intents=intents)


# ai_chatbot モジュールのインポート（埋め込みデータが存在する場合のみ）
# 注意: 遅延ロードにより、実際のデータロードは初回応答時に行われます
generate_response = None
# データベースが存在すればチャットボット機能を有効化
if os.path.exists(DB_PATH):
    try:
        from ai_chatbot import generate_response

        print("✅ AIチャットボット機能が有効化されました")
        print("   💡 モデルとデータは初回応答時に自動的にロードされます")

        # APIキーの確認
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key and api_key.strip():
            print("   🧠 Google Gemini APIを使用した応答生成が有効です")
        else:
            print("   ⚠️ 警告: GEMINI_API_KEYが設定されていません")
            print("   💡 GEMINI_API_KEY環境変数を設定してください")
    except Exception as e:
        print(f"❌ AIチャットボットのロード中にエラーが発生しました: {e}")
        generate_response = None


@client.event
async def on_ready():
    print("✅ ログイン成功")
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
        # スラッシュコマンドらしき入力を検出した場合は案内メッセージを表示
        if query.startswith("/"):
            await message.channel.send(
                "スラッシュコマンドは単独で入力する必要があります。\n"
                "メンションや `!ask` を使用する場合は、質問内容のみを入力してください（スラッシュは不要です）。"
            )
            return
        if os.path.exists(DB_PATH) and generate_response:
            # LLMを使用して返信を生成
            try:
                # 初回初期化の責任をai_chatbotモジュール側に持たせる
                from ai_chatbot import ensure_initialized_with_callback

                loading_msg = None

                def on_first_init():
                    """初回初期化開始時のコールバック"""
                    # この時点ではasyncコンテキスト外なので、メッセージ送信は後で行う

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

                # Discord の 2000 文字制限チェック
                if len(response) > 2000:
                    # 2000文字を超える場合は切り詰めて警告を追加
                    response = (
                        response[:1950] + "\n\n...（応答が長すぎるため省略されました）"
                    )

                await message.channel.send(response)
            except ValueError as e:
                # APIキー未設定または類似メッセージ未検出
                await message.channel.send(f"⚠️ 設定エラー: {str(e)}")
            except RuntimeError as e:
                # LLM API応答取得失敗
                await message.channel.send(f"⚠️ APIエラー: {str(e)}")
            except Exception as e:
                await message.channel.send(f"⚠️ エラーが発生しました: {str(e)}")
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
