from config import BOT_TOKEN

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix="/", help_command=None, intents=disnake.Intents.all())

# Словарь для хранения ролей и смайликов для каждого сообщения
message_data = {}


@bot.command()
async def command(ctx, *, data: str):
    # Разделяем данные по символу "|"
    parts = data.split("|")

    # Первая часть - текст сообщения
    text = parts[0].strip()

    # Вторая часть - смайлики
    emojis = [emoji.strip() for emoji in parts[1].split() if emoji.strip()]

    # Третья часть - роли
    roles = [role.strip() for role in parts[2].split() if role.strip()]
    roles = [int(role[3:-1]) for role in roles]

    message = await ctx.send(f"{text}")


    # Добавляем реакции к сообщению
    for emoji in emojis:
        await message.add_reaction(emoji)

    # Сохраняем роли и смайлики для этого сообщения

    emoji_role_dict = {disnake.PartialEmoji(name=emoji): role for emoji, role in zip(emojis, roles)}
    message_data[message.id] = emoji_role_dict
    print(message_data)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")

@bot.event
async def on_raw_reaction_add(payload):

    # Проверяем, что реакция была добавлена на сообщение бота
    if payload.guild_id is None or payload.member is None:
        return

    # Проверяем что это сообщение для реакций
    if payload.message_id not in message_data:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Check if we're still in the guild and it's cached.
        return

    try:
        role_id = message_data[payload.message_id][payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        print("Роль не найдена")
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    try:
        # Finally, add the role.
        await payload.member.add_roles(role)
    except disnake.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass



@bot.event
async def on_raw_reaction_remove(payload):
    # Проверяем, что реакция была добавлена на сообщение бота
    if payload.guild_id is None:
        return

    # Проверяем что это сообщение для реакций
    if payload.message_id not in message_data:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        # Check if we're still in the guild and it's cached.
        return

    try:
        role_id = message_data[payload.message_id][payload.emoji]
    except KeyError:
        # If the emoji isn't the one we care about then exit as well.
        print("Роль не найдена")
        return

    role = guild.get_role(role_id)
    if role is None:
        # Make sure the role still exists and is valid.
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        # Make sure the member still exists and is valid.
        return

    try:
        # Finally, add the role.
        await member.remove_roles(role)
    except disnake.HTTPException:
        # If we want to do something in case of errors we'd do it here.
        pass


if __name__ == "__main__":
    bot.run(BOT_TOKEN)  # Замените 'YOUR_TOKEN' на ваш токен бота

