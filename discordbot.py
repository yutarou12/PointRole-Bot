import discord
from discord.ext import commands
import json
import traceback
import os
from asyncio import new_event_loop
from aiosqlite import connect

loop = new_event_loop()

with open("config.json", "r") as f:
    config = json.load(f)

bot = commands.Bot(
    command_prefix=config["PREFIX"],
    intents=discord.Intents.all(),
    help_command=None
)

extensions = [
    'extensions.bot',
    'extensions.utils',
]
for extension in extensions:
    bot.load_extension(extension)


async def db():
    try:
        if not os.path.exists("./db/data.db"):
            open(f"./db/data.db", "w").close()
            async with connect('./db/data.db') as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
                    count = await cur.fetchone()

                    if count[0] == 0:
                        await cur.execute("CREATE TABLE point_data(guild_id BIGINT(20), user_id BIGINT(20), point INT);")
                        await conn.commit()

                        await cur.execute("CREATE TABLE guild_data(guild_id BIGINT(20) PRIMARY KEY , r_1_0 BIGINT(20),  r_1_1 BIGINT(20), r_1_2 BIGINT(20), r_1_3 BIGINT(20), r_1_4 BIGINT(20), r_1_5 BIGINT(20), r_1_6 BIGINT(20), r_1_7 BIGINT(20), r_1_8 BIGINT(20), r_1_9 BIGINT(20), r_2_0 BIGINT(20), r_2_1 BIGINT(20), r_2_2 BIGINT(20), r_2_3 BIGINT(20), r_2_4 BIGINT(20), r_2_5 BIGINT(20), r_2_6 BIGINT(20), r_2_7 BIGINT(20), r_2_8 BIGINT(20), r_2_9 BIGINT(20), r_3_0 BIGINT(20), r_3_1 BIGINT(20), r_3_2 BIGINT(20), r_3_3 BIGINT(20), r_3_4 BIGINT(20), r_3_5 BIGINT(20), r_3_6 BIGINT(20), r_3_7 BIGINT(20), r_3_8 BIGINT(20), r_3_9 BIGINT(20));")
                        await conn.commit()
    except:
        appinfo = await bot.application_info()
        await appinfo.owner.send(f"エラー情報\n```\n{traceback.format_exc()}\n```")


@bot.event
async def on_ready():
    print(f"{bot.user.name} でログインしました")
    await bot.change_presence(activity=discord.Game(name=f"Prefix: {bot.command_prefix}", type=1))


@bot.event
async def cog_command_error(self, ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        embed = discord.Embed(
            title="⚠ 権限エラー",
            description="あなたにはこのコマンドを実行する権限がありません"
        )
        return await ctx.send(embed=embed)
    else:
        orig_error = getattr(error, "original", error)
        error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())

        err_embed = discord.Embed(title="エラー発生",
                                  description="予測不能なエラーが発生しました。\n時間をおいても解決しない場合は、以下のエラーIDと一緒にお問い合わせください。")
        err_embed.add_field(name="エラーID", value=f"`{ctx.message.id}`")
        await ctx.send(embed=err_embed)

        appinfo = await bot.application_info()
        embed = discord.Embed(title="エラー情報",
                              description=f"```\n{error_msg}\n```")
        embed.set_footer(text=f"G: {ctx.guild.name} | ID: {ctx.message.id}")
        await appinfo.owner.send(embed=embed)


if __name__ == '__main__':
    main_task = loop.create_task(db())
    loop.run_until_complete(main_task)
    loop.close()
    bot.run(config["DISCORD_BOT_TOKEN"])
