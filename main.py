import discord
from discord.ext import commands
import json
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Pega o diretório onde o main.py está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# O arquivo config.json pode estar um nível acima (local) ou no mesmo diretório (Discloud)
CONFIG_PATH = os.path.join(BASE_DIR, '..', 'config.json')
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')

# Carregando as configurações do JSON
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Configurando as intenções do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Criando a instância do bot
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)
bot.config = config # Armazena o config para ser usado pelos Cogs

@bot.event
async def on_ready():
    print("\n\033[35m" + "="*50)
    print(" V O G U E   B O T   O N L I N E ".center(50))
    print("="*50 + "\033[0m")
    print(f"\n \033[36mBot:\033[0m {bot.user.name}")
    print(f" \033[36mID:\033[0m {bot.user.id}")
    print(f" \033[36mPrefixo:\033[0m {bot.command_prefix}")
    print(f" \033[36mStatus:\033[0m Conectado com sucesso ao Discord!\n")
    print("\033[35m" + "-"*50 + "\033[0m")
    
    # Pasta de Cogs relativa ao main.py
    COGS_DIR = os.path.join(BASE_DIR, 'cogs')
    
    # Adiciona o BASE_DIR ao sys.path para facilitar imports internos nos cogs
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    for filename in os.listdir(COGS_DIR):
        if filename.endswith('.py'):
            try:
                # Carrega a extensão usando o caminho absoluto/relativo correto
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f" \033[32mMódulo carregado:\033[0m {filename}")
            except Exception as e:
                print(f" \033[31mFalha ao carregar:\033[0m {filename} -> {e}")
                
    print("\033[35m" + "-"*50 + "\033[0m\n")

# Iniciando o bot
token = os.environ.get('TOKEN') or config.get('token')
bot.run(token)
