#!/usr/bin/env python3
"""
Discord メッセージ取得スクリプト

指定されたDiscordサーバーから過去のメッセージを取得し、
data/messages.json に保存します。
"""

import discord
import json
import os
import sys
from datetime import datetime

# 環境変数から設定を読み取る
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD_ID_STR = os.environ.get('TARGET_GUILD_ID')

# データ保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_PATH = os.path.join(DATA_DIR, 'messages.json')

# デフォルト設定
DEFAULT_MESSAGE_LIMIT = 1000  # 各チャンネルから取得する最大メッセージ数

def validate_environment():
    """環境変数の検証"""
    if not TOKEN:
        print('❌ エラー: 環境変数 DISCORD_TOKEN が設定されていません')
        return False
    
    if not GUILD_ID_STR:
        print('❌ エラー: 環境変数 TARGET_GUILD_ID が設定されていません')
        return False
    
    try:
        int(GUILD_ID_STR)
    except ValueError:
        print('❌ エラー: TARGET_GUILD_ID が無効な形式です（数値である必要があります）')
        return False
    
    return True

def ensure_data_directory():
    """dataディレクトリの存在を確認し、必要に応じて作成"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f'📁 dataディレクトリを作成しました: {DATA_DIR}')

async def fetch_messages_from_guild(client, guild_id, message_limit=DEFAULT_MESSAGE_LIMIT):
    """
    指定されたギルドからメッセージを取得
    
    Args:
        client: Discord Client
        guild_id: ギルドID
        message_limit: 各チャンネルから取得する最大メッセージ数
    
    Returns:
        メッセージのリスト
    """
    guild = client.get_guild(guild_id)
    
    if guild is None:
        try:
            guild = await client.fetch_guild(guild_id)
        except discord.NotFound:
            print('❌ エラー: 指定されたギルドが見つかりません')
            print('   Botがこのサーバーに参加していない可能性があります')
            return None
        except discord.Forbidden:
            print('❌ エラー: ギルド情報へのアクセスが拒否されました')
            print('   Botに必要な権限がない可能性があります')
            return None
    
    print(f'✅ ギルド "{guild.name}" に接続しました')
    print(f'📊 チャンネル数: {len(guild.text_channels)}')
    print()
    
    all_messages = []
    
    for channel in guild.text_channels:
        print(f'📝 チャンネル #{channel.name} からメッセージを取得中...')
        
        try:
            messages = []
            async for message in channel.history(limit=message_limit):
                # Botのメッセージはスキップ
                if message.author.bot:
                    continue
                
                # メッセージ内容が空の場合はスキップ
                if not message.content.strip():
                    continue
                
                messages.append({
                    'id': message.id,
                    'channel_id': channel.id,
                    'channel_name': channel.name,
                    'author_id': message.author.id,
                    'author_name': str(message.author),
                    'content': message.content,
                    'created_at': message.created_at.isoformat(),
                    'timestamp': message.created_at.timestamp()
                })
            
            all_messages.extend(messages)
            print(f'   → {len(messages)}件のメッセージを取得')
            
        except discord.Forbidden:
            print(f'   ⚠️  スキップ: アクセス権限がありません')
        except Exception as e:
            print(f'   ⚠️  エラー: {e}')
    
    print()
    print(f'✅ 合計 {len(all_messages)}件のメッセージを取得しました')
    
    return all_messages

async def main():
    """メイン処理"""
    print('=' * 60)
    print('Discord メッセージ取得スクリプト')
    print('=' * 60)
    print()
    
    # 環境変数の検証
    if not validate_environment():
        sys.exit(1)
    
    # dataディレクトリの準備
    ensure_data_directory()
    
    # Discord Clientのセットアップ
    intents = discord.Intents.default()
    intents.guilds = True
    intents.message_content = True
    intents.members = True
    
    client = discord.Client(intents=intents)
    
    guild_id = int(GUILD_ID_STR)
    success = False
    
    @client.event
    async def on_ready():
        nonlocal success
        
        print(f'🤖 Bot "{client.user}" としてログインしました')
        print()
        
        try:
            # メッセージの取得
            messages = await fetch_messages_from_guild(client, guild_id)
            
            if messages is None:
                await client.close()
                return
            
            if len(messages) == 0:
                print('⚠️  警告: メッセージが1件も取得できませんでした')
                print('   以下の点を確認してください:')
                print('   - Botがサーバーに参加しているか')
                print('   - Botにメッセージ履歴を読む権限があるか')
                print('   - チャンネルにメッセージが存在するか')
                await client.close()
                return
            
            # メッセージをJSONファイルに保存
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            print(f'💾 メッセージを保存しました: {OUTPUT_PATH}')
            print()
            print('=' * 60)
            print('✅ メッセージ取得が完了しました')
            print('=' * 60)
            print()
            print('次のステップ:')
            print('  1. python src/prepare_dataset.py を実行して埋め込みデータを生成')
            print('  2. python src/main.py を実行してBotを起動')
            print()
            
            success = True
            
        except Exception as e:
            print(f'❌ エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await client.close()
    
    # Botの起動
    try:
        await client.start(TOKEN)
    except discord.LoginFailure:
        print('❌ エラー: 認証に失敗しました')
        print('   DISCORD_TOKENが無効です。正しいトークンを設定してください。')
        sys.exit(1)
    except Exception as e:
        print(f'❌ エラー: 接続中に問題が発生しました: {e}')
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
