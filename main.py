import os
import time
import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_languages = {}

IDIOMAS_NOM = {
    "es": "Español ES",
    "en": "English US",
    "pt": "Português BR",
    "fr": "Français FR",
    "de": "Deutsch DE",
    "it": "Italiano IT",
    "ja": "Japonés JP",
    "ko": "Coreano KR",
    "zh-cn": "Chino CN",
    "ru": "Ruso RU",
    "ar": "Árabe AR"
}

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Bot conectado como {bot.user} y comandos sincronizados ({len(synced)}).")
    except Exception as e:
        print(e)

@bot.tree.context_menu(name="Traducir para mí")
async def traducir_mensaje(interaction: discord.Interaction, message: discord.Message):
    idioma_destino = user_languages.get(interaction.user.id, "es")

    if not message.content:
        await interaction.response.send_message("El mensaje seleccionado no contiene texto para traducir.", ephemeral=True)
        return

    try:
        # Intento de traducción con reintento automático si hay saturación
        resultado = None
        for intento in range(3):
            try:
                resultado = GoogleTranslator(source='auto', target=idioma_destino).translate(message.content)
                break
            except Exception:
                if intento == 2:
                    raise
                time.sleep(1)

        nombre_idioma = IDIOMAS_NOM.get(idioma_destino, idioma_destino)
        await interaction.response.send_message(
            f"🌐 **Traducción privada ({nombre_idioma}):**\n{resultado}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"El servicio de traducción está temporalmente ocupado. Por favor, intenta de nuevo en unos segundos.", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
