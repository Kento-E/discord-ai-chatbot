import os

import discord
from discord import app_commands

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
            print(
                "   Bot自体は動作しますが、/modeコマンドが使用できない可能性があります"
            )


client = MyClient(intents=intents)


def is_llm_mode_enabled():
    """
    LLMモードが有効かどうかを判定

    Returns:
        bool: GEMINI_API_KEYが設定されている場合True、そうでない場合False
    """
    llm_api_key = os.environ.get("GEMINI_API_KEY")
    return llm_api_key is not None and llm_api_key.strip() != ""


# ai_agent モジュールのインポート（埋め込みデータが存在する場合のみ）
# 注意: 遅延ロードにより、実際のデータロードは初回応答時に行われます
generate_response = None
if os.path.exists(EMBED_PATH):
    try:
        from ai_agent import generate_response

        print("✅ AIエージェント機能が有効化されました")
        print("   💡 モデルとデータは初回応答時に自動的にロードされます")

        # LLMモードの確認
        if is_llm_mode_enabled():
            print(
                "   🧠 LLMモード: Google Gemini APIを使用した応答生成が有効です"
            )
        else:
            print("   ⚠️ 警告: GEMINI_API_KEYが設定されていません")
            print(
                "   💡 このBotはLLMモード専用です。GEMINI_API_KEY環境変数を設定してください"
            )
    except Exception as e:
        print(f"❌ AIエージェントのロード中にエラーが発生しました: {e}")
        generate_response = None


@client.event
async def on_ready():
    print("✅ ログイン成功")
    print("🤖 Botが起動し、メッセージの受信を開始しました")
    if generate_response:
        print("💬 メンションまたは !ask コマンドで質問できます")
    print("📋 /mode コマンドでBot状態を確認できます")


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
                "スラッシュコマンド（例: `/mode`）は単独で入力する必要があります。\n"
                "メンションや `!ask` を使用する場合は、質問内容のみを入力してください（スラッシュは不要です）。"
            )
            return
        if os.path.exists(EMBED_PATH) and generate_response:
            # LLMを使用して返信を生成
            try:
                # 初回初期化の責任をai_agentモジュール側に持たせる
                from ai_agent import ensure_initialized_with_callback

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

                await message.channel.send(response)
            except ValueError as e:
                # API key not set or no similar messages
                await message.channel.send(f"⚠️ 設定エラー: {str(e)}")
            except RuntimeError as e:
                # LLM API failed
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


@client.tree.command(name="mode", description="Botの状態を確認します")
async def mode_command(interaction: discord.Interaction):
    """Botの状態（利用可否）を表示するスラッシュコマンド"""
    try:
        # APIキーの設定確認
        has_api_key = is_llm_mode_enabled()

        # 知識データの有無を確認
        has_knowledge_data = os.path.exists(EMBED_PATH)

        # 埋め込みを作成
        embed = discord.Embed(
            title="🤖 Bot状態",
            color=discord.Color.blue(),
            description="現在のBotの状態を表示します",
        )

        # Bot状態の判定
        if not generate_response:
            status = "❌ **利用不可**"
            status_description = "知識データが未生成のため、Botは動作していません。"
        elif not has_api_key:
            status = "⚠️ **設定不足**"
            status_description = (
                "GEMINI_API_KEYが設定されていません。\n"
                "環境変数GEMINI_API_KEYを設定してください。"
            )
        else:
            status = "✅ **利用可能**"
            status_description = (
                "Google Gemini APIを使用して応答を生成します。\n"
                "過去メッセージを文脈として活用します。"
            )

        embed.add_field(name="状態", value=status, inline=False)
        embed.add_field(name="詳細", value=status_description, inline=False)

        # 知識データの状態
        if has_knowledge_data:
            knowledge_status = "✅ 利用可能"
        else:
            knowledge_status = "❌ 未生成"

        embed.add_field(name="知識データ", value=knowledge_status, inline=True)

        # APIキーの状態
        if has_api_key:
            api_key_status = "✅ 設定済み"
        else:
            api_key_status = "❌ 未設定"

        embed.add_field(name="APIキー", value=api_key_status, inline=True)

        # フッター情報
        if not generate_response:
            footer_text = "知識データを生成してください"
        elif not has_api_key:
            footer_text = "GEMINI_API_KEY環境変数を設定してください"
        else:
            footer_text = "Botは正常に動作しています"
        embed.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        # エラーハンドリング: インタラクションが3秒以内に応答されないことを防ぐ
        await interaction.response.send_message(
            f"⚠️ エラーが発生しました: {str(e)}", ephemeral=True
        )


if __name__ == "__main__":
    client.run(TOKEN)
