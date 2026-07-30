import discord
from discord.ext import commands

class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        config = self.bot.config
        
        # Ignora comandos inexistentes
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Erro de falta de cargo específico (ex: Nuke)
        if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
            emoji_erro = config['emojis']['erro']
            cor_rosa = discord.Color(config['colors']['sucesso']) # Cor rosa solicitada
            
            embed = discord.Embed(
                description=f"{emoji_erro} Você não possui permissão para utilizar este comando.",
                color=cor_rosa
            )
            return await ctx.send(embed=embed)
        
        # Outros erros genéricos
        emoji_erro = config['emojis']['erro']
        cor_erro = discord.Color(config['colors']['erro'])
        
        embed = discord.Embed(
            description=f"{emoji_erro} Ocorreu um erro ao executar este comando:\n`{str(error)}`",
            color=cor_erro
        )
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Eventos(bot))
