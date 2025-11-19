import discord
import os

EMBED_PATH = os.path.join(os.path.dirname(__file__), '../data/embeddings.json')

# 環境変数から機密情報を読み取る
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD_ID_STR = os.environ.get('TARGET_GUILD_ID')

if not TOKEN:
	raise ValueError('環境変数 DISCORD_TOKEN が設定されていません')
if not GUILD_ID_STR:
	raise ValueError('環境変数 TARGET_GUILD_ID が設定されていません')

GUILD_ID = int(GUILD_ID_STR)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# ai_agent モジュールのインポート（埋め込みデータが存在する場合のみ）
generate_response = None
if os.path.exists(EMBED_PATH):
	try:
		from ai_agent import generate_response
		print('AIエージェント機能が正常にロードされました。')
	except Exception as e:
		print(f'AIエージェントのロード中にエラーが発生しました: {e}')
		generate_response = None

@client.event
async def on_ready():
	print(f'Logged in as {client.user}')
	print('Bot is running and ready to answer.')

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	# Botへのメンション or !ask コマンドで応答
	if client.user in message.mentions or message.content.startswith('!ask '):
		query = message.content.replace('!ask ', '').replace(f'<@{client.user.id}>', '').strip()
		if not query:
			await message.channel.send('質問内容を入力してください。')
			return
		if os.path.exists(EMBED_PATH) and generate_response:
			# 予測返信を生成
			try:
				response = generate_response(query)
				await message.channel.send(response)
			except Exception as e:
				await message.channel.send(f'エラーが発生しました: {str(e)}')
		else:
			help_msg = (
				'知識データが未生成です。まずメッセージ取得・整形を行ってください。\n'
				'\n'
				'**手順:**\n'
				'1. `python src/fetch_messages.py` でメッセージ取得\n'
				'2. `python src/prepare_dataset.py` で埋め込みデータ生成\n'
				'3. Botを再起動\n'
				'\n'
				'詳細は docs/USAGE.md またはREADMEをご覧ください。'
			)
			await message.channel.send(help_msg)

if __name__ == '__main__':
	client.run(TOKEN)