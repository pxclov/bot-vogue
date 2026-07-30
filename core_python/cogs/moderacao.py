import discord
from discord.ext import commands
import asyncio

class ConfirmAction(discord.ui.View):
    """View genérica de confirmação para ações de moderação."""
    def __init__(self, ctx, target, config, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.target = target
        self.config = config
        self.value = None

        # Configura os botões a partir do config
        self.btn_confirmar.emoji = self.config['emojis']['sucesso']
        self.btn_cancelar.emoji = self.config['emojis']['erro']

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                f"{self.config['emojis']['erro']} Apenas {self.ctx.author.mention} pode confirmar esta ação.", 
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def btn_confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def btn_cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = False
        self.stop()

class Moderacao(commands.Cog):
    """Módulo de Moderação - Hierarquia, Ban e Unban."""
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.command(name="ban")
    @commands.has_any_role(1516977870994407555, 1516976266064957441)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member = None):
        """Bane um usuário respeitando a hierarquia de cargos."""
        try:
            await ctx.message.delete()
        except:
            pass

        if not member:
            return await ctx.send(f"{self.config['emojis']['erro']} Mencione um usuário para banir.", delete_after=5)

        # Confirmação
        embed_confirma = discord.Embed(
            title="VOGUE - CONFIRMAÇÃO DE BANIMENTO",
            description=f"{self.config['emojis']['atencao']} **Deseja banir {member.mention} (ID: {member.id})?**\nEsta ação é permanente.",
            color=discord.Color(self.config['colors']['sucesso'])
        )
        view = ConfirmAction(ctx, member, self.config)
        msg = await ctx.send(embed=embed_confirma, view=view)

        await view.wait()
        if view.value is True:
            try:
                await member.ban(reason=f"Banido por {ctx.author}")
                embed_ok = discord.Embed(description=f"{self.config['emojis']['sucesso']} O usuário **{member.name}** foi banido.", color=discord.Color(self.config['colors']['sucesso']))
                await msg.edit(embed=embed_ok, view=None)
            except Exception as e:
                await ctx.send(f"Erro: {e}", delete_after=10)
        else:
            await msg.delete()

    @commands.command(name="unban")
    @commands.has_any_role(1516977870994407555, 1516976266064957441)
    @commands.guild_only()
    async def unban(self, ctx, user_id: str = None):
        """Desbane um usuário pelo ID ou Nome."""
        try:
            await ctx.message.delete()
        except:
            pass

        if not user_id:
            return await ctx.send(f"{self.config['emojis']['erro']} Forneça o ID ou Nome do usuário para desbanir.", delete_after=5)

        # Busca na lista de banidos
        ban_entry = None
        async for entry in ctx.guild.bans():
            user = entry.user
            if user_id == str(user.id) or user_id.lower() == str(user).lower():
                ban_entry = entry
                break
        
        if not ban_entry:
            return await ctx.send(f"{self.config['emojis']['erro']} Usuário não encontrado na lista de banidos.", delete_after=10)

        target_user = ban_entry.user

        # Embed de Confirmação
        embed_unban = discord.Embed(
            title="VOGUE - CONFIRMAÇÃO DE DESBANIMENTO",
            description=(
                f"{self.config['emojis']['atencao']} **Você tem certeza que deseja desbanir o usuário {target_user.name} (ID: {target_user.id})?**\n\n"
                "Ele poderá retornar ao servidor imediatamente."
            ),
            color=discord.Color(self.config['colors']['sucesso'])
        )
        
        view = ConfirmAction(ctx, target_user, self.config)
        msg_unban = await ctx.send(embed=embed_unban, view=view)

        await view.wait()

        if view.value is True:
            try:
                await ctx.guild.unban(target_user, reason=f"Desbanido por {ctx.author}")
                embed_sucesso = discord.Embed(
                    description=f"{self.config['emojis']['sucesso']} O usuário **{target_user.name}** foi desbanido com sucesso.",
                    color=discord.Color(self.config['colors']['sucesso'])
                )
                await msg_unban.edit(embed=embed_sucesso, view=None)
            except Exception as e:
                await ctx.send(f"Erro ao desbanir: {e}", delete_after=10)
        else:
            await msg_unban.delete()

async def setup(bot):
    await bot.add_cog(Moderacao(bot))
