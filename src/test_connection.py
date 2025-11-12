#!/usr/bin/env python3
"""
Discord Secrets疎通テストスクリプト

DISCORD_TOKENとTARGET_GUILD_IDの有効性を検証します。
"""

import os
import sys
import discord


# 詳細情報を保存するグローバル変数
detailed_info = {
    'bot_name': None,
    'bot_id': None,
    'guild_name': None,
    'guild_id': None,
    'member_count': None
}


def output_detailed_info():
    """詳細情報をGitHub Step Summaryに出力"""
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if not summary_file:
        return
    
    try:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write('\n---\n\n')
            f.write('## 📋 詳細情報（リポジトリのActions権限を持つユーザーが閲覧可能）\n\n')
            
            if detailed_info['bot_name']:
                f.write(f"**Bot名**: {detailed_info['bot_name']}\n\n")
            if detailed_info['bot_id']:
                f.write(f"**Bot ID**: {detailed_info['bot_id']}\n\n")
            if detailed_info['guild_name']:
                f.write(f"**サーバー名**: {detailed_info['guild_name']}\n\n")
            if detailed_info['guild_id']:
                f.write(f"**サーバーID**: {detailed_info['guild_id']}\n\n")
            if detailed_info['member_count'] is not None:
                f.write(f"**メンバー数**: {detailed_info['member_count']}\n\n")
            
            f.write('> ⚠️ この情報はリポジトリのActionsタブにアクセスできるユーザーが閲覧できます。\n')
            f.write('> 公開ログには表示されません。\n')
    except Exception as e:
        print(f'⚠️ 詳細情報の出力中にエラーが発生しました: {e}')


def test_connection():
    """Discord APIとの疎通を確認する"""
    
    # 環境変数の取得
    token = os.environ.get('DISCORD_TOKEN')
    guild_id_str = os.environ.get('TARGET_GUILD_ID')
    show_details = os.environ.get('SHOW_DETAILS', 'false').lower() == 'true'
    
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
        print('❌ エラー: TARGET_GUILD_ID が無効な形式です（数値である必要があります）')
        return False
    
    print('📝 環境変数の確認:')
    print(f'  - DISCORD_TOKEN: {"設定済み" if token else "未設定"} (長さ: {len(token) if token else 0})')
    print(f'  - TARGET_GUILD_ID: 設定済み')
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
            # 詳細情報を保存（show_detailsがtrueの場合のみstep summaryに出力）
            if show_details:
                detailed_info['bot_name'] = str(client.user)
                detailed_info['bot_id'] = client.user.id
            
            print('✅ Discord接続成功: Bot認証完了')
            print()
            
            # ギルドの取得
            guild = client.get_guild(guild_id)
            
            if guild is None:
                # get_guildで取得できない場合、fetch_guildを試す
                try:
                    guild = await client.fetch_guild(guild_id)
                except discord.NotFound:
                    error_message = '指定されたギルドが見つかりません'
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
            
            # 詳細情報を保存（show_detailsがtrueの場合のみstep summaryに出力）
            if show_details:
                detailed_info['guild_name'] = guild.name
                detailed_info['guild_id'] = guild.id
                detailed_info['member_count'] = guild.member_count if guild.member_count else "不明"
            
            print('✅ ギルド確認成功: アクセス権限を確認しました')
            print()
            
            success = True
            print('🎉 すべての疎通テストに成功しました！')
            
            # 詳細情報を出力（show_detailsがtrueの場合）
            if show_details:
                output_detailed_info()
            
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
