import discord
from discord.ext import commands
from datetime import datetime

class Logs(commands.Cog):
    """Módulo de monitoramento e registros do servidor (Logs)."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    def get_log_channel(self, guild, channel_key):
        """Busca o canal de log pelo ID configurado no config.json."""
        channel_id = self.config.get('channels', {}).get(channel_key)
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    def format_time(self):
        """Retorna o horário atual formatado para exibição."""
        return datetime.now().strftime('%d/%m/%Y às %H:%M:%S')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Registra a entrada de membros."""
        canal = self.get_log_channel(member.guild, 'log_entrada')
        if not canal: return

        emoji_log = self.config['emojis'].get('log', )
        emoji_seta = self.config['emojis'].get('seta_branca', )
        emoji_membro = self.config['emojis'].get('membro_branco', )
        emoji_check = self.config['emojis'].get('verificado_branco',)

        embed = discord.Embed(
            title=f"{emoji_log} REGISTRO DE ENTRADA",
            description=f"{emoji_check} O usuário **{member.name}** entrou no servidor.",
            color=0x00FF00 # Verde
        )
        embed.add_field(name=f"{emoji_membro} Informações", value=f"{emoji_seta} **Nome:** {member.display_name}\n{emoji_seta} **User:** {member.name}\n{emoji_seta} **ID:** `{member.id}`", inline=False)
        embed.set_footer(text=f"Entrou em: {self.format_time()}")
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Registra a saída de membros."""
        canal = self.get_log_channel(member.guild, 'log_saida')
        if not canal: return

        emoji_log = self.config['emojis'].get('log', )
        emoji_seta = self.config['emojis'].get('seta_branca',)
        emoji_membro = self.config['emojis'].get('membro_branco', )
        emoji_erro = self.config['emojis'].get('errado_branco',)

        embed = discord.Embed(
            title=f"{emoji_log} REGISTRO DE SAÍDA",
            description=f"{emoji_erro} O usuário **{member.name}** saiu (ou foi expulso) do servidor.",
            color=0xFF0000 # Vermelho
        )
        embed.add_field(name=f"{emoji_membro} Informações", value=f"{emoji_seta} **Nome:** {member.display_name}\n{emoji_seta} **User:** {member.name}\n{emoji_seta} **ID:** `{member.id}`", inline=False)
        embed.set_footer(text=f"Saiu em: {self.format_time()}")
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Registra banimentos."""
        canal = self.get_log_channel(guild, 'log_ban')
        if not canal: return

        emoji_log = self.config['emojis'].get('log',)
        emoji_seta = self.config['emojis'].get('seta_branca',)
        emoji_membro = self.config['emojis'].get('membro_branco',)
        emoji_ban = self.config['emojis'].get('ban',)

        embed = discord.Embed(
            title=f"{emoji_log} REGISTRO DE BANIMENTO",
            description=f"{emoji_ban} O usuário **{user.name}** foi **BANIDO** do servidor.",
            color=0x8B0000 # Vermelho Escuro
        )
        embed.add_field(name=f"{emoji_membro} Informações do Banido", value=f"{emoji_seta} **Nome:** {user.display_name}\n{emoji_seta} **User:** {user.name}\n{emoji_seta} **ID:** `{user.id}`", inline=False)
        embed.set_footer(text=f"Banido em: {self.format_time()}")
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Registra entradas, saídas e trocas de canal de voz."""
        emoji_log = self.config['emojis'].get('log', )
        emoji_seta = self.config['emojis'].get('seta_branca',)
        emoji_ponto = self.config['emojis'].get('ponto_branco',)

        # Entrou em um canal de voz (não estava em nenhum antes)
        if before.channel is None and after.channel is not None:
            canal_log = self.get_log_channel(member.guild, 'log_entrada_call')
            if canal_log:
                embed = discord.Embed(
                    title=f"{emoji_log} ENTRADA EM CALL",
                    description=f"{emoji_seta} O membro **{member.mention}** entrou em um canal de voz.",
                    color=0x00FF00
                )
                embed.add_field(name="Canal", value=f"{emoji_ponto} {after.channel.mention}", inline=False)
                embed.set_footer(text=f"User ID: {member.id} • {self.format_time()}")
                await canal_log.send(embed=embed)

        # Saiu de um canal de voz (não está em nenhum agora)
        elif before.channel is not None and after.channel is None:
            canal_log = self.get_log_channel(member.guild, 'log_saida_call')
            if canal_log:
                embed = discord.Embed(
                    title=f"{emoji_log} SAÍDA DE CALL",
                    description=f"{emoji_seta} O membro **{member.mention}** desconectou-se do canal de voz.",
                    color=0xFF0000
                )
                embed.add_field(name="Canal Anterior", value=f"{emoji_ponto} {before.channel.name}", inline=False)
                embed.set_footer(text=f"User ID: {member.id} • {self.format_time()}")
                await canal_log.send(embed=embed)

        # Trocou de canal de voz
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            # Mandar log na saída e na entrada, ou só em um deles (ex: entrada_call para a troca)
            canal_log = self.get_log_channel(member.guild, 'log_entrada_call')
            if canal_log:
                embed = discord.Embed(
                    title=f"{emoji_log} TROCA DE CALL",
                    description=f"{emoji_seta} O membro **{member.mention}** mudou de canal de voz.",
                    color=0xFFFF00 # Amarelo
                )
                embed.add_field(name="De", value=f"{emoji_ponto} {before.channel.name}", inline=True)
                embed.add_field(name="Para", value=f"{emoji_ponto} {after.channel.mention}", inline=True)
                embed.set_footer(text=f"User ID: {member.id} • {self.format_time()}")
                await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Registra mensagens apagadas (incluindo tentativas de salvar mídias)."""
        if message.author.bot:
            return

        canal = self.get_log_channel(message.guild, 'log_mensagem_apagada')
        if not canal: return

        emoji_log = self.config['emojis'].get('log',)
        emoji_seta = self.config['emojis'].get('seta_branca',)
        emoji_lixeira = self.config['emojis'].get('lixeira',)

        embed = discord.Embed(
            title=f"{emoji_log} MENSAGEM APAGADA",
            description=f"{emoji_lixeira} Uma mensagem de **{message.author.mention}** foi apagada no canal {message.channel.mention}.",
            color=0xFFA500 # Laranja
        )

        # Adiciona o conteúdo do texto, se houver
        if message.content:
            conteudo = message.content
            if len(conteudo) > 1000:
                conteudo = conteudo[:1000] + "... [MENSAGEM MUITO LONGA]"
            embed.add_field(name="Conteúdo", value=f"```\n{conteudo}\n```", inline=False)
        else:
            embed.add_field(name="Conteúdo", value="*Mensagem sem texto.*", inline=False)

        # Checa por anexos
        if message.attachments:
            links = []
            for anexo in message.attachments:
                # O Discord apaga os links de cache rapidamente, mas enviamos mesmo assim
                # para que fique registrado qual era o nome do arquivo enviado.
                links.append(f"[{anexo.filename}]({anexo.url})")
            
            anexos_str = "\n".join(links)
            embed.add_field(name="Anexos (Mídia/GIF)", value=f"A mensagem continha {len(message.attachments)} anexo(s):\n{anexos_str}\n*(Nota: O Discord desativa o link de anexos apagados logo em seguida)*", inline=False)
        
        embed.set_footer(text=f"User ID: {message.author.id} • {self.format_time()}")
        await canal.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Logs(bot))
