import discord
from discord import app_commands
from discord.ui import TextInput, Modal, View, Button

# ⚠️ СРОЧНО: Сбрось этот токен в Discord Developer Portal и вставь новый!
TOKEN = "MTU1MzA5MzEwODAxNzkyMjIxOQ.GxFUkD.3quIWtP26fMimT8in6s6VDyos1r8XDtIXXy1UY"
TARGET_CHANNEL_ID = 1562158488170528848

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


class ReviewModal(Modal, title="Оставить отзыв"):
    def __init__(self, bot_client):
        super().__init__()
        self.bot_client = bot_client

        self.nickname = TextInput(label="Ваш никнейм", min_length=1, max_length=64)
        self.product = TextInput(label="Каким продуктом пользовались?", min_length=1, max_length=100)
        self.rating = TextInput(label="Оценка от 1 до 10", min_length=1, max_length=2)
        self.comment = TextInput(label="Что вам понравилось или не понравилось?", style=discord.TextStyle.long,
                                 min_length=1, max_length=2000)

        self.add_item(self.nickname)
        self.add_item(self.product)
        self.add_item(self.rating)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        # Используем переданный клиент для получения канала
        channel = self.bot_client.get_channel(TARGET_CHANNEL_ID)

        if not channel:
            # Если канал не найден, пишем в тот канал, откуда вызвали модалку (для отладки)
            await interaction.response.send_message(
                f"❌ Канал для отзывов (ID: {TARGET_CHANNEL_ID}) не найден. Проверьте права бота и ID.",
                ephemeral=True
            )
            return

        embed = discord.Embed(title="🗣 Новый отзыв", color=discord.Color.blurple())
        embed.add_field(name="Никнейм", value=self.nickname.value, inline=False)
        embed.add_field(name="Продукт", value=self.product.value, inline=False)
        embed.add_field(name="Оценка (1–10)", value=self.rating.value, inline=False)
        embed.add_field(name="Комментарий", value=self.comment.value, inline=False)
        embed.set_footer(text=f"От: {interaction.user.display_name} ({interaction.user.id})")

        try:
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Спасибо за отзыв!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ У бота нет прав на отправку сообщений в канал отзывов.",
                                                    ephemeral=True)


class ReviewView(View):
    def __init__(self, bot_client):
        super().__init__(timeout=None)
        self.bot_client = bot_client

    @discord.ui.button(label="Оставить отзыв", style=discord.ButtonStyle.blurple, custom_id="review_button")
    async def review_callback(self, interaction: discord.Interaction, button: Button):
        # Передаем client в модалку
        await interaction.response.send_modal(ReviewModal(self.bot_client))


@tree.command(name="setreviewbtn", description="Разместить кнопку для отзывов в канале")
async def set_review_btn(interaction: discord.Interaction):
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Канал для отзывов не найден. Проверьте ID.", ephemeral=True)
        return

    # Передаем client в View
    await channel.send(view=ReviewView(client))
    await interaction.response.send_message("✅ Кнопка размещена в канале отзывов.", ephemeral=True)


@client.event
async def on_ready():
    print(f"Бот запущен как {client.user}")
    try:
        synced = await tree.sync()
        print(f"✅ Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")


client.run(TOKEN)
