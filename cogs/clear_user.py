import discord
from discord.ext import commands

class UtilidadesPrivacidade(commands.Cog):
    """Módulo de Privacidade - Comandos de Limpeza Silenciosa e Gatilhos sem Prefixo."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ouvinte para capturar o gatilho 'tomalerda' sem necessidade de prefixo."""
        if message.author.bot:
            return

        # Verifica se o conteúdo da mensagem é exatamente 'tomalerda' (sem prefixo)
        if message.content.lower() == "tomalerda":
            # Executa a limpeza silenciosa para o autor da mensagem
            await self.executar_limpeza(message.channel, message.author, message)
        if message.content.lower() == "cl":
            # Executa a limpeza silenciosa para o autor da mensagem
            await self.executar_limpeza(message.channel, message.author, message)

    @commands.command(name="cl")
    @commands.guild_only()
    async def cl(self, ctx):
        """Ghost Mode: Apaga as últimas mensagens do próprio autor no canal (Requer Prefixo)."""
        await self.executar_limpeza(ctx.channel, ctx.author, ctx.message)

    async def executar_limpeza(self, channel, author, trigger_message):
        """Lógica centralizada de limpeza silenciosa."""
        # 1. Deleta a mensagem que ativou o comando
        try:
            await trigger_message.delete()
        except:
            pass

        # 2. Define o filtro: Apenas mensagens do autor do comando
        def is_author(m):
            return m.author == author

        # 3. Executa a limpeza em Ghost Mode
        try:
            # Varre as últimas 500 mensagens do canal em busca de mensagens do autor
            await channel.purge(limit=500, check=is_author)
        except (discord.Forbidden, discord.HTTPException):
            # Falha silenciosa
            pass

async def setup(bot):
    await bot.add_cog(UtilidadesPrivacidade(bot))
