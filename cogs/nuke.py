import discord
from discord.ext import commands
import asyncio
from utils.embeds import EmbedVogue

class ConfirmNuke(discord.ui.View):
    """View para confirmação do comando nuke com botões interativos (Estilo vogue)."""
    def __init__(self, ctx, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.config = ctx.bot.config
        self.value = None

        # Botão Confirmar: Estilo Verde (success)
        self.btn_confirmar = discord.ui.Button(
            label="Confirmar",
            style=discord.ButtonStyle.success,
            emoji=discord.PartialEmoji.from_str(self.config['emojis'].get('verificado_branco', '✅'))
        )
        self.btn_confirmar.callback = self.confirmar_callback
        self.add_item(self.btn_confirmar)

        # Botão Cancelar: Estilo Vermelho (danger)
        self.btn_cancelar = discord.ui.Button(
            label="Cancelar",
            style=discord.ButtonStyle.danger,
            emoji=discord.PartialEmoji.from_str(self.config['emojis'].get('errado_branco'))
        )
        self.btn_cancelar.callback = self.cancelar_callback
        self.add_item(self.btn_cancelar)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Apenas o autor do comando pode interagir com os botões
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                f"{self.config['emojis']['erro']} Apenas {self.ctx.author.mention} pode utilizar estes botões.",
                ephemeral=True
            )
            return False
        return True

    async def confirmar_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.value = True
        self.stop()
        
        try:
            channel = interaction.channel
            old_position = channel.position # Guarda a posição original
            
            # Clona o canal mantendo as mesmas permissões
            new_channel = await channel.clone(reason=f"Nuke solicitado por {interaction.user}")
            
            # Move o novo canal para a posição exata do antigo
            await new_channel.edit(position=old_position)
            
            # Formata a mensagem de sucesso usando o padrão vogue
            dados = {
                "Operação": "Nuke concluído",
                "Responsável": interaction.user.mention,
                "Status": "Canal redefinido com sucesso"
            }
            desc = EmbedVogue.format_description(dados)
            embed = EmbedVogue.clean_embed(title="vogue - Gestão de Canais", description=desc)
            
            # Apaga o canal antigo e envia a mensagem no novo
            await channel.delete(reason="Canal nukado")
            await new_channel.send(embed=embed)
            
        except discord.Forbidden:
            await interaction.followup.send(
                f"{self.config['emojis']['erro']} Erro: O bot não possui permissões suficientes para gerir este canal.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"{self.config['emojis']['erro']} Ocorreu um erro inesperado: {e}",
                ephemeral=True
            )

    async def cancelar_callback(self, interaction: discord.Interaction):
        self.value = False
        self.stop()
        
        # Desativa os botões para evitar cliques repetidos
        for item in self.children:
            item.disabled = True
            
        embed = interaction.message.embeds[0]
        embed.description = f"{self.config['emojis']['erro']} Nuke cancelado."
        # Mantém a estética rosa mas sinaliza o erro na descrição
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        # Se os botões ainda estiverem ativos (não clicados)
        if self.value is None:
            for item in self.children:
                item.disabled = True
            # Nota: O tratamento visual do timeout é feito no comando principal após o wait()

class Administracao(commands.Cog):
    """Módulo de comandos de administração avançada para o vogue."""
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.command(name="nuke")
    @commands.has_any_role(1516977870994407555, 1516976266064957441) # Apenas quem tem estes cargos específicos
    @commands.guild_only()
    async def nuke(self, ctx):
        """Redefine o canal atual (apaga mensagens e clonagem)."""
        
        emoji_atencao = self.config['emojis']['atencao']
        # Cor obrigatória: Rosa do servidor (sucesso)
        cor_rosa = discord.Color(self.config['colors']['sucesso'])
        
        embed = discord.Embed(
            title="VOGUE - SISTEMA NUKE",
            description=(
                f"{emoji_atencao} **Tem certeza que deseja nukar este canal?**\n\n"
            ),
            color=cor_rosa
        )
        embed.set_footer(text="Aguardando confirmação • 30 segundos")
        
        # Adiciona a imagem do banner (VOGUE)
        if 'banners' in self.config and 'nuke' in self.config['banners']:
            embed.set_image(url=self.config['banners']['nuke'])

        view = ConfirmNuke(ctx)
        prompt = await ctx.send(embed=embed, view=view)
        
        # Aguarda a resposta ou o tempo esgotar
        await view.wait()
        
        if view.value is None:
            # Caso o tempo de 30s tenha esgotado
            for item in view.children:
                item.disabled = True
            
            embed.description = f"{self.config['emojis']['erro']} Tempo esgotado."
            await prompt.edit(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Administracao(bot))
