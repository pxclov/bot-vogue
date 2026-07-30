from discord.ext import commands
from utils.embeds import EmbedVogue

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        # Criando conteúdo estruturado conforme o novo padrão
        dados = {
            "Status": "Operacional",
            "Latência": f"{round(self.bot.latency * 1000)}ms"
        }
        
        description = EmbedVogue.format_description(dados)
        embed = EmbedVogue.clean_embed(title="vogue - Teste de Conexão", description=description)
        
        await ctx.send(embed=embed)

    @commands.command(name="all")
    @commands.has_any_role(1509618787874246726)
    async def all_command(self, ctx):
        cargo_id = 1495236811675533359
        cargo = ctx.guild.get_role(cargo_id)
        
        if cargo:
            try:
                await ctx.author.add_roles(cargo)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(Comandos(bot))
