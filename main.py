import os
import discord
from discord.ext import commands
from discord import app_commands
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario temporal para guardar el idioma de cada usuario
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

# Vista con menú desplegable (Select Menu) para elegir el idioma
class SelectIdiomaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(
        placeholder="Selecciona tu idioma de traducción...",
        min_values=1,
        max_values=1,
        options=[discord.SelectOption(label=nombre, value=codigo) for codigo, nombre in IDIOMAS_NOM.items()]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        user_languages[interaction.user.id] = select.values[0]
        nombre_Elegido = IDIOMAS_NOM.get(select.values[0])
        await interaction.response.send_message(f"✅ ¡Tu idioma predeterminado se ha cambiado a **{nombre_Elegido}**!", ephemeral=True)

# Comando de barra para abrir el selector de idioma
@bot.tree.command(name="idioma", description="Configura tu idioma preferido para las traducciones")
async def idioma(interaction: discord.Interaction):
    view = SelectIdiomaView()
    await interaction.response.send_message("Selecciona en el menú de abajo el idioma al que deseas traducir:", view=view, ephemeral=True)

# Menú contextual (clic derecho en un mensaje)
@bot.tree.context_menu(name="Traducir para mí")
async def traducir_mensaje(interaction: discord.Interaction, message: discord.Message):
    idioma_destino = user_languages.get(interaction.user.id, "es")

    if not message.content:
        await interaction.response.send_message("El mensaje seleccionado no contiene texto para traducir.", ephemeral=True)
        return

    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": idioma_destino,
            "dt": "t",
            "q": message.content
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        traduccion = "".join([sentence[0] for sentence in data[0]])
        nombre_idioma = IDIOMAS_NOM.get(idioma_destino, idioma_destino)
        
        await interaction.response.send_message(
            f"🌐 **Traducción privada ({nombre_idioma}):**\n{traduccion}",
            ephemeral=True
        )
    except Exception as e:
        print(f"Error: {e}")
        await interaction.response.send_message("Ocurrió un error al procesar la traducción. Inténtalo de nuevo en unos segundos.", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
