import os
import discord
from discord.ext import commands
from discord import app_commands
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para guardar el idioma preferido de cada usuario
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

# Evento para traducir automáticamente cada mensaje nuevo
@bot.event
async def on_message(message):
    # Evitar que el bot responda a sus propios mensajes para prevenir bucles
    if message.author.bot:
        return

    # Verificar si el usuario configuró un idioma (si no, por defecto español)
    idioma_destino = user_languages.get(message.author.id)

    if idioma_destino and message.content:
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
            
            # Enviar la traducción de forma privada (ephemeral no se puede en on_message directo, 
            # así que se envía al canal etiquetando al usuario o por mensaje directo)
            await message.channel.send(
                f"🌐 **Traducción automática para {message.author.mention} ({nombre_idioma}):**\n{traduccion}"
            )
        except Exception as e:
            print(f"Error en traducción automática: {e}")

    # Permitir que los comandos de barra sigan funcionando
    await bot.process_commands(message)

# Vista con menú desplegable para elegir el idioma
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
        nombre_elegido = IDIOMAS_NOM.get(select.values[0])
        await interaction.response.send_message(f"✅ ¡Idioma configurado para traducción automática: **{nombre_elegido}**!", ephemeral=True)

# Comando de barra para abrir el selector de idioma
@bot.tree.command(name="idioma", description="Configura tu idioma preferido para las traducciones automáticas")
async def idioma(interaction: discord.Interaction):
    view = SelectIdiomaView()
    await interaction.response.send_message("Selecciona en el menú de abajo el idioma al que deseas que se traduzcan los mensajes:", view=view, ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
