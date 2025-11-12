#!/usr/bin/env python3
"""
Discord Secrets疎通テストスクリプト

DISCORD_TOKENとTARGET_GUILD_IDの有効性を検証します。
"""

import os
import sys
import discord


def test_connection():
    """Discord APIとの疎通を確認する"""
    
    # 環境変数の取得
    token = os.environ.get('DISCORD_TOKEN')
    guild_id_str = os.environ.get('TARGET_GUILD_ID')
    
    # 環境変数の存在確認
    if not token:
        print('❌ エラー: 環境変数 DISCORD_TOKEN が設定されていません')
        return False
    
    if not guild_id_str:
        print('❌ エラー: 環境変数 TARGET_GUILD_ID が設定されていません')
        return False
    
    # GUILD_IDの形式確認
    try:
        guild_id = int(guild_id_str)
    except ValueError:
        print(f'❌ エラー: TARGET_GUILD_ID が無効な形式です: {guild_id_str}')
        return False
    
    print('📝 環境変数の確認:')
    print(f'  - DISCORD_TOKEN: {"設定済み" if token else "未設定"} (長さ: {len(token) if token else 0})')
    print(f'  - TARGET_GUILD_ID: {guild_id}')
    print()
    
    # Discord Clientのセットアップ
    intents = discord.Intents.default()
    intents.guilds = True
    client = discord.Client(intents=intents)
    
    success = False
    error_message = None
    
    @client.event
    async def on_ready():
        nonlocal success, error_message
        try:
            print(f'✅ Discord接続成功: {client.user}')
            print(f'   ユーザーID: {client.user.id}')
            print()
            
            # ギルドの取得
            guild = client.get_guild(guild_id)
            
            if guild is None:
                # get_guildで取得できない場合、fetch_guildを試す
                try:
                    guild = await client.fetch_guild(guild_id)
                except discord.NotFound:
                    error_message = f'指定されたギルドが見つかりません: {guild_id}'
                    print(f'❌ エラー: {error_message}')
                    print('   Botがこのサーバーに参加していない可能性があります')
                    await client.close()
                    return
                except discord.Forbidden:
                    error_message = 'ギルド情報へのアクセスが拒否されました'
                    print(f'❌ エラー: {error_message}')
                    print('   Botに必要な権限がない可能性があります')
                    await client.close()
                    return
            
            print(f'✅ ギルド確認成功:')
            print(f'   名前: {guild.name}')
            print(f'   ID: {guild.id}')
            print(f'   メンバー数: {guild.member_count if guild.member_count else "不明"}')
            print()
            
            success = True
            print('🎉 すべての疎通テストに成功しました！')
            
        except Exception as e:
            error_message = str(e)
            print(f'❌ 予期しないエラーが発生しました: {error_message}')
        finally:
            await client.close()
    
    @client.event
    async def on_error(event, *args, **kwargs):
        nonlocal error_message
        error_message = f'イベント処理中にエラーが発生しました: {event}'
        print(f'❌ {error_message}')
    
    # Botの起動
    print('🔄 Discord APIへの接続を試みています...')
    try:
        client.run(token)
    except discord.LoginFailure:
        print('❌ エラー: 認証に失敗しました')
        print('   DISCORD_TOKENが無効です。正しいトークンを設定してください。')
        return False
    except Exception as e:
        print(f'❌ エラー: 接続中に問題が発生しました: {e}')
        return False
    
    return success


if __name__ == '__main__':
    result = test_connection()
    sys.exit(0 if result else 1)
