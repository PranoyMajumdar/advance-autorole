from configs import TOKEN
import discord
from discord.ext import commands
from mongo import autorole_db

intents = discord.Intents.default()
intents.message_content = True  # For the message content intent


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def on_ready(self):
        print("Subscribe to CodeWithPranoy!")


bot = MyBot()


@bot.group(name='autorole')
async def autorole(ctx: commands.Context):
    return


@autorole.command(name='enable')
async def enable(ctx: commands.Context):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        return await ctx.send("Autorole already enabled!")

    autorole_db.insert_one(
        {"_id": str(ctx.guild.id), "humans": [], "bots": []})
    await ctx.send("Autorole enabled!")


@autorole.command(name='disable')
async def disable(ctx: commands.Context):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        autorole_db.delete_one({"_id": str(ctx.guild.id)})
        return await ctx.send("Autorole disabled!")

    return await ctx.send("Autorole is not enabled!")


@autorole.group(name='add')
async def add(ctx: commands.Context):
    return


@autorole.group(name='remove')
async def remove(ctx: commands.Context):
    return


@add.command(name='humans')
async def add_humans(ctx: commands.Context, role: discord.Role):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        autorole_db.update_one({"_id": str(ctx.guild.id)}, {
                               "$push": {"humans": role.id}})
        return await ctx.send(f"Successfully added **{role.name}** to humans autorole list.")

    return await ctx.send("Autorole is not enabled!")


@add.command(name='bots')
async def add_bots(ctx: commands.Context, role: discord.Role):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        autorole_db.update_one({"_id": str(ctx.guild.id)}, {
                               "$push": {"bots": role.id}})
        return await ctx.send(f"Successfully added **{role.name}** to bots autorole list.")

    return await ctx.send("Autorole is not enabled!")


@remove.command(name='humans')
async def remove_humans(ctx: commands.Context, role: discord.Role):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        roles = list(find['humans'])
        if role.id in roles:
            autorole_db.update_one({"_id": str(ctx.guild.id)}, {
                                   "$pull": {"humans": role.id}})
            return await ctx.send(f"**{role.name}** successfully removed from humans autoroles list!")
        return await ctx.send(f"**{role.name}** not in humans autoroles!")
    return await ctx.send("Autorole is not enabled!")


@remove.command(name='bots')
async def remove_bots(ctx: commands.Context, role: discord.Role):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        roles = list(find['bots'])
        if role.id in roles:
            autorole_db.update_one({"_id": str(ctx.guild.id)}, {
                                   "$pull": {"bots": role.id}})
            return await ctx.send(f"**{role.name}** successfully removed from bots autorole list!")

    return await ctx.send("Autorole is not enabled!")


@autorole.command(name='show')
async def show(ctx: commands.Context):
    if (find := autorole_db.find_one({"_id": str(ctx.guild.id)})):
        humans = list(find['humans'])
        bots = list(find['bots'])

        fetched_humans: list = []
        fetched_bots: list = []
        for i in humans:
            role = ctx.guild.get_role(i)
            if role is not None:
                fetched_humans.append(role)

        for i in bots:
            role = ctx.guild.get_role(i)
            if role is not None:
                fetched_bots.append(role)

        print(fetched_humans)
        print(fetched_bots)
        return await ctx.send(embed=discord.Embed(
            title=f"{ctx.guild.name}'s Autorole List"
        ).add_field(
            name='Humans', value='\n'.join(i.mention for i in fetched_humans)
        ).add_field(
            name='Bots', value='\n'.join(i.mention for i in fetched_bots)
        )
        )

    return await ctx.send("Autorole is not enabled!")


@bot.event
async def on_member_join(member: discord.Member):
    if(find:=autorole_db.find_one({"_id": str(member.guild.id)})):
        humans: list = find['humans']
        bots: list = find['bots']

        fetched_humans: list = []
        fetched_bots: list = []
        if humans:
            for i in humans:
                role = member.guild.get_role(i)
                if role is not None:
                    fetched_humans.append(role)
        if bots:
            for i in bots:
                role = member.guild.get_role(i)
                if role is not None:
                    fetched_bots.append(role)

        for i in fetched_humans:
            if not member.bot:
                await member.add_roles(i)

        for i in fetched_bots:
            if member.bot:
                await member.add_roles(i)

    return


@autorole.command(name='test')
async def ar_test(ctx: commands.Context):
    await on_member_join(ctx.author)
if __name__ == '__main__':
    bot.run(TOKEN)
