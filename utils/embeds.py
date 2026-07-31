import discord
import json
import os

# Tenta encontrar o config.json em diferentes níveis dependendo do ambiente (Local vs Discloud)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config.json')
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config.json')
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')


with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

class EmbedVogue:
    """Classe responsável por padronizar o visual de todas as embeds do bot vogue."""
    
    @staticmethod
    def clean_embed(title=None, description=None):
        # Usando a cor rosa (sucesso) definida no seu config.json
        cor_rosa = discord.Color(config['colors']['sucesso'])
        
        # Título sempre em CAIXA ALTA conforme solicitado
        display_title = title.upper() if title else None
        
        embed = discord.Embed(
            title=display_title,
            description=description,
            color=cor_rosa
        )
        
        # Configuração da Thumbnail (Imagem pequena no canto superior)
        if 'banners' in config and 'logo' in config['banners']:
            embed.set_thumbnail(url=config['banners']['logo'])
        
        # Configuração do Banner (Imagem grande na base)
        if 'banners' in config and 'nuke' in config['banners']:
            embed.set_image(url=config['banners']['nuke'])
        
        # Rodapé clean
        embed.set_footer(text="vogue • santori")
        
        return embed

    @staticmethod
    def format_description(linhas):
        """
        Auxiliar para formatar a descrição com bullet points
        seguindo a hierarquia estética do vogue.
        """
        # Usando o novo emoji de seta para uma hierarquia mais limpa
        emoji_seta = config['emojis'].get('seta', config['emojis']['sucesso'])
        
        corpo_texto = ""
        for titulo, info in linhas.items():
            # Título da seção em negrito e info abaixo com o emoji de seta
            corpo_texto += f"\n**{titulo.upper()}:**\n{emoji_seta} {info}\n"
        return corpo_texto
