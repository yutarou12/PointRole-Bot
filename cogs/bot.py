import math
from discord import Embed
from discord.ext import commands


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! - WebSocket Latency : {math.floor(self.bot.latency * 1000)} ms")

    @commands.command()
    async def help(self, ctx, args=None):
        if not args:
            embed = Embed(title="Bot Help")
            embed.add_field(name="Botコマンド", value="`help`, `ping`")
            embed.add_field(name="Pointコマンド", value="`add`, `unset`, `setup`")
            await ctx.send(embed=embed)
        elif args == "help":
            embed = Embed(title="Bot Help",
                          description="**コマンド** : help\n```\nこのBotのヘルプを表示します\n```")
            await ctx.send(embed=embed)
        elif args == "ping":
            embed = Embed(title="Bot Help",
                          description="**コマンド** : ping\n```\nこのBotのPingを表示します\n```")
            await ctx.send(embed=embed)
        elif args == "add":
            embed = Embed(title="Bot Help",
                          description="**コマンド** : add\n```\nポイントを指定した人に配布します\n```")
            await ctx.send(embed=embed)
        elif args == "unset":
            embed = Embed(title="Bot Help",
                          description="**コマンド** : unset\n```\nこのBotが作成した役職を削除し、サーバーの設定を初期化します\n```")
            await ctx.send(embed=embed)
        elif args == "setup":
            embed = Embed(title="Bot Help",
                          description="**コマンド** : setup\n```\nポイント用役職を作成し、セットアップを行います\n```")
            await ctx.send(embed=embed)
