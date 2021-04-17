from discord.ext import commands
from aiosqlite import connect
import re
import discord
import time
import asyncio


async def write_db(ctx, userdata, point):
    async with connect('./db/data.db') as conn:
        async with conn.cursor() as cur:
            await conn.commit()
            await cur.execute("SELECT user_id,point FROM point_data WHERE guild_id=? AND user_id=?;",
                              (ctx.guild.id, userdata.id))
            db_result = await cur.fetchone()
            if db_result:

                new_point = int(db_result[1]) + int(point)
                await cur.execute("UPDATE point_data SET point=? WHERE guild_id=? AND user_id=?",
                                  (new_point, ctx.guild.id, userdata.id))
                await conn.commit()
                await cur.execute("SELECT user_id,point FROM point_data WHERE guild_id=? AND user_id=?;",
                                  (ctx.guild.id, userdata.id))
                new_db_result = await cur.fetchone()
                user_name = ctx.guild.get_member(new_db_result[0])
                embed_up = discord.Embed(title="ポイントアップ！",
                                         description=f"{user_name.mention} のポイントが {new_db_result[1]} になりました")
                await ctx.send(embed=embed_up)
            else:
                await cur.execute("INSERT INTO point_data values(?,?,?)",
                                  (ctx.guild.id, userdata.id, int(point)))
                await conn.commit()
                user_name = ctx.guild.get_member(userdata.id)
                embed_new = discord.Embed(title="ポイントアップ！",
                                          description=f"{user_name.mention} のポイントが {point} になりました")
                await ctx.send(embed=embed_new)


async def add_point(ctx, user_data):
    async with connect('./db/data.db') as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM guild_data WHERE guild_id=?", (ctx.guild.id,))
            db_response = await cur.fetchone()
            if db_response:
                db_role_list = []
                for n in range(1, 31):
                    db_role_list.append(db_response[n])
                # pointの取得
                await cur.execute("SELECT point FROM point_data WHERE guild_id=? AND user_id=?",
                                  (ctx.guild.id, user_data.id))
                user_res = await cur.fetchone()
                # 役職のremove
                for role in user_data.roles:
                    if role.id in db_role_list:
                        await user_data.remove_roles(role)
                # 役職の追加
                point_list = list(str(user_res[0]))
                if len(point_list) == 1:
                    role_id = db_role_list[20 + int(point_list[0])]
                    get_role_data = ctx.guild.get_role(role_id)

                    if get_role_data:
                        await user_data.add_roles(get_role_data)

                elif len(point_list) == 2:
                    role_id_1 = db_role_list[10 + int(point_list[0])]
                    role_id_2 = db_role_list[20 + int(point_list[1])]

                    get_role_data_1 = ctx.guild.get_role(int(role_id_1))
                    get_role_data_2 = ctx.guild.get_role(int(role_id_2))

                    if get_role_data_1 and get_role_data_2:
                        await user_data.add_roles(get_role_data_1)
                        await user_data.add_roles(get_role_data_2)

                elif len(point_list) == 3:
                    role_id_1 = db_role_list[int(point_list[0])]
                    role_id_2 = db_role_list[10 + int(point_list[1])]
                    role_id_3 = db_role_list[20 + int(point_list[2])]

                    get_role_data_1 = ctx.guild.get_role(role_id_1)
                    get_role_data_2 = ctx.guild.get_role(role_id_2)
                    get_role_data_3 = ctx.guild.get_role(role_id_3)

                    if get_role_data_1 and get_role_data_2 and get_role_data_3:
                        await user_data.add_roles(get_role_data_1)
                        await user_data.add_roles(get_role_data_2)
                        await user_data.add_roles(get_role_data_3)
                else:
                    get_role_data_1 = ctx.guild.get_role(db_role_list[9])
                    get_role_data_2 = ctx.guild.get_role(db_role_list[19])
                    get_role_data_3 = ctx.guild.get_role(db_role_list[29])

                    if get_role_data_1 and get_role_data_2 and get_role_data_3:
                        await user_data.add_roles(get_role_data_1)
                        await user_data.add_roles(get_role_data_2)
                        await user_data.add_roles(get_role_data_3)
                db_role_list.clear()


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def add(self, ctx, user=None, point=None):
        if not user:
            await ctx.send("ユーザーはメンション又は、IDで指定してください")
        elif not point:
            await ctx.send("ポイント数は数字で指定してください")
        elif not point.isdecimal():
            return await ctx.send("ポイント数は数字で指定してください")
        else:
            if ctx.message.mentions:
                for u in ctx.message.mentions:
                    user_info = ctx.guild.get_member(u.id)
                    if user_info:
                        message = ctx
                        user_data = user_info
                        point_data = point
                        await write_db(message, user_data, point_data)
                        await add_point(message, user_data)
                    else:
                        await ctx.send("メンバーが見つかりませんでした")

            else:
                result = re.compile('[0-9]{18}').match(user)
                if result is None:
                    await ctx.send("ユーザーはメンション又は、IDで指定してください")
                else:
                    user_info = ctx.guild.get_member(int(user))
                    if user_info:
                        message = ctx
                        user_data = user_info
                        point_data = point
                        await write_db(message, user_data, point_data)
                        await add_point(message, user_data)
                    else:
                        print("見つかりませんでした")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setup(self, ctx):
        async with connect('./db/data.db') as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM guild_data WHERE guild_id=?", (ctx.guild.id,))
                db_response = await cur.fetchone()
                if not db_response:

                    embed = discord.Embed(description="セットアップを行う場合は y 、キャンセルする場合は n を送信してください。")
                    b_setup_msg = await ctx.send(embed=embed)

                    def check(message):
                        if message.author == ctx.author and message.content in ["y", "n"]:
                            return message.content

                    msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                    if msg.content == "y":

                        await msg.delete()
                        embed = discord.Embed(title="次のセットアップを実行中です...", description="・ポイント用役職(30個)を作成")
                        await b_setup_msg.edit(embed=embed)

                        role_add_list = ["(百の位)", "(十の位)", "(一の位)"]
                        role_create_list = []
                        for role_name_list in role_add_list:
                            for num in range(10):
                                role_create = await ctx.guild.create_role(name=f"{num}")
                                role_create_list.append(role_create.id)
                                time.sleep(1)

                        print(role_create_list)
                        rl = role_create_list
                        await cur.execute("INSERT INTO guild_data values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                          (ctx.guild.id, rl[0], rl[1], rl[2], rl[3], rl[4], rl[5], rl[6], rl[7], rl[8], rl[9], rl[10], rl[11], rl[12], rl[13], rl[14], rl[15], rl[16], rl[17], rl[18], rl[19], rl[20], rl[21], rl[22], rl[23], rl[24], rl[25], rl[26], rl[27], rl[28], rl[29]))
                        await conn.commit()
                        await b_setup_msg.edit(embed=discord.Embed(description="完了しました"))
                        role_create_list.clear()
                else:
                    await ctx.send(embed=discord.Embed(description="既に設定されています"))

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def unset(self, ctx):
        v_embed = discord.Embed(description="設定を削除するにはy、キャンセルする場合はnを送信してください\n削除すると設定が初期化され、役職が削除されます")
        v_msg = await ctx.send(embed=v_embed)

        def check(message):
            if message.author == ctx.author and message.content in ["y", "n"]:
                return message.content

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            if msg.content == "y":
                await v_msg.edit(embed=discord.Embed(description="設定を削除中です..."))
                await msg.delete()
                db_role_list = []
                async with connect('./db/data.db') as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT * FROM guild_data WHERE guild_id=?", (ctx.guild.id,))
                        db_response = await cur.fetchone()
                        if db_response:
                            for n in range(1, 31):
                                db_role_list.append(db_response[n])
                            for role_id in db_role_list:
                                role = ctx.guild.get_role(int(role_id))
                                if role:
                                    try:
                                        await role.delete()
                                    except:
                                        pass
                            await cur.execute("DELETE FROM guild_data WHERE guild_id=?;", (ctx.guild.id,))
                            await conn.commit()
                            await v_msg.edit(embed=discord.Embed(description="設定の初期化が完了しました"))
                        else:
                            await v_msg.edit(embed=discord.Embed(description="設定されていません"))
                        db_role_list.clear()
            elif msg.content == "n":
                return await v_msg.edit(embed=discord.Embed(description="操作をキャンセルしました"))

        except asyncio.TimeoutError:
            embed = discord.Embed(description=f"30秒以内にメッセージが送信されなかったためタイムアウトしました。")
            await v_msg.edit(embed=embed)
