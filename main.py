import os
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_languages = {}

IDIOMAS_NOM = {
    "es": "Español 🇪🇸",
    "en": "English 🇺🇸",
    "pt": "Português 🇧🇷",
    "fr": "Français 🇫🇷",
    "de": "Deutsch 🇩🇪",
    "it": "Italiano 🇮🇹",
    "ja": "Japonés 🇯🇵",
    "ko": "Coreano 🇰🇷",
    "zh-cn": "Chino 🇨🇳",
    "ru": "Ruso 🇷🇺",
    "ar": "Árabe 🇸🇦",
    "hi": "Hindi 🇮🇳",
    "tr": "Turco 🇹🇷",
    "nl": "Holandés 🇳🇱",
    "pl": "Polaco 🇵🇱"
}

class SelectorIdioma(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Español", value="es", emoji="🇪🇸"),
            discord.SelectOption(label="English", value="en", emoji="🇺🇸"),
            discord.SelectOption(label="Português", value="pt", emoji="🇧🇷"),
            discord.SelectOption(label="Français", value="fr", emoji="🇫🇷"),
            discord.SelectOption(label="Deutsch", value="de", emoji="🇩🇪"),
            discord.SelectOption(label="Italiano", value="it", emoji="🇮🇹"),
            discord.SelectOption(label="日本語 (Japonés)", value="ja", emoji="🇯🇵"),
            discord.SelectOption(label="한국어 (Coreano)", value="ko", emoji="🇰🇷"),
            discord.SelectOption(label="中文 (Chino)", value="zh-cn", emoji="🇨🇳"),
            discord.SelectOption(label="Русский (Ruso)", value="ru", emoji="🇷🇺"),
            discord.SelectOption(label="العربية (Árabe)", value="ar", emoji="🇸🇦"),
            discord.SelectOption(label="Hindi", value="hi", emoji="🇮🇳"),
            discord.SelectOption(label="Türkçe", value="tr", emoji="🇹🇷"),
            discord.SelectOption(label="Nederlands", value="nl", emoji="🇳🇱"),
            discord.SelectOption(label="Polski", value="pl", emoji="🇵🇱"),
        ]
        super().__init__(placeholder="Elige tu idioma preferido para traducciones...", options=options)

    async def callback(self, interaction: discord.Interaction):
        user_languages[interaction.user.id] = self.values[0]
        nombre_idioma = IDIOMAS_NOM.get(self.values[0], self.values[0])
        await interaction.response.send_message(
            f"✅ **Idioma guardado.** A partir de ahora, tus traducciones privadas se mostrarán en **{nombre_idioma}**.",
            ephemeral=True
        )

class VistaIdioma(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectorIdioma())

@bot.event
async def on_ready():
    print(f"Bot listo y conectado como: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados ({len(synced)} comandos registrados).")
    except Exception as e:
        print(f"Error sincronizando comandos: {e}")

@bot.tree.command(name="idioma", description="Configura tu idioma personal de traducción privada")
async def comando_idioma(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Selecciona el idioma al que deseas que traduzcas tus mensajes de forma privada:",
        view=VistaIdioma(),
        ephemeral=True
    )

@bot.tree.command(name="decir", description="Envía un texto que el bot repetirá en el canal")
@app_commands.describe(texto="El mensaje que deseas que el bot publique")
async def comando_decir(interaction: discord.Interaction, texto: str):
    await interaction.response.send_message("Mensaje enviado con éxito.", ephemeral=True)
    await interaction.channel.send(texto)

@bot.tree.context_menu(name="Traducir para mí")
async def traducir_mensaje(interaction: discord.Interaction, message: discord.Message):
    idioma_destino = user_languages.get(interaction.user.id, "es")
    
    if not message.content:
        await interaction.response.send_message("El mensaje seleccionado no contiene texto para traducir.", ephemeral=True)
        return

    try:
        resultado = GoogleTranslator(source='auto', target=idioma_destino).translate(message.content)
        nombre_idioma = IDIOMAS_NOM.get(idioma_destino, idioma_destino)
        await interaction.response.send_message(
            f"🌐 **Traducción privada ({nombre_idioma}):**\n{resultado}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"Ocurrió un error al traducir el mensaje: {e}", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))