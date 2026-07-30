import discord
from discord.ext import commands
import asyncio
import json
import os
import io

class ComentarioModal(discord.ui.Modal, title='Deixe seu comentário'):
    comentario = discord.ui.TextInput(
        label='Escreva seu comentário',
        style=discord.TextStyle.paragraph,
        placeholder='Nossa, que vídeo incrível!',
        required=True,
        max_length=1000
    )

    def __init__(self, author_id, author_name, config):
        super().__init__()
        self.author_id = author_id
        self.author_name = author_name
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        try:
            autor = await interaction.client.fetch_user(self.author_id)
            if autor and not autor.bot:
                cor = int(self.config['colors']['sucesso'], 16) if isinstance(self.config['colors']['sucesso'], str) else self.config['colors']['sucesso']
                embed_dm = discord.Embed(
                    title="VOGUE - NOTIFICAÇÃO TIKTOK",
                    description=f"💬 **{interaction.user.name}** comentou no seu vídeo!\n\n> {self.comentario.value}",
                    color=cor
                )
                await autor.send(embed=embed_dm)
            await interaction.response.send_message("✅ Seu comentário foi enviado para o autor do vídeo!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("❌ Houve um erro ao enviar seu comentário (talvez a DM do autor esteja fechada).", ephemeral=True)


class TikTok(commands.Cog):
    """Módulo TikTok - Exclusivo para vídeos com sistema de interações completo."""
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.data_path = os.path.join(os.path.dirname(__file__), "tiktok.json")
        self.ttk_data = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r") as f:
                    data = json.load(f)
                    return {
                        str(msg_id): {
                            "curtir": set(info.get("curtir", [])),
                            "republicar": set(info.get("republicar", [])),
                            "salvar": set(info.get("salvar", []))
                        } for msg_id, info in data.items()
                    }
            except Exception:
                return {}
        return {}

    def save_data(self):
        try:
            data = {
                str(msg_id): {
                    "curtir": list(info["curtir"]),
                    "republicar": list(info["republicar"]),
                    "salvar": list(info["salvar"])
                } for msg_id, info in self.ttk_data.items()
            }
            with open(self.data_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro ao salvar tiktok.json: {e}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        custom_id = interaction.data.get('custom_id')
        if not custom_id or not custom_id.startswith("ttk_"):
            return

        parts = custom_id.split(":")
        acao = parts[0]
        
        try:
            author_id = int(parts[1])
            author_name = parts[2] if len(parts) > 2 else "Usuário"
        except:
            author_id = None
            author_name = "Usuário"

        message = interaction.message
        message_id = str(message.id)
        user_id = interaction.user.id

        if message_id not in self.ttk_data:
            self.ttk_data[message_id] = {"curtir": set(), "republicar": set(), "salvar": set()}

        # -- AÇÃO COMENTAR -- (Precisa abrir Modal, então deve vir primeiro antes do edit_message)
        if acao == "ttk_comentar":
            modal = ComentarioModal(author_id=author_id, author_name=author_name, config=self.config)
            await interaction.response.send_modal(modal)
            return

        # -- DEMAIS AÇÕES --
        msg_feedback = ""
        is_new = False
        
        # Ação baseada no custom_id
        tipo_acao = acao.replace("ttk_", "")  # curtir, republicar, salvar, apagar

        if tipo_acao in ["curtir", "republicar", "salvar"]:
            if user_id in self.ttk_data[message_id][tipo_acao]:
                self.ttk_data[message_id][tipo_acao].remove(user_id)
                msg_feedback = f"Você removeu o seu {tipo_acao}."
            else:
                self.ttk_data[message_id][tipo_acao].add(user_id)
                msg_feedback = f"Você clicou em {tipo_acao} no vídeo! ✅"
                is_new = True

            # Atualiza os contadores nos botões
            view = discord.ui.View.from_message(message)
            for item in view.children:
                if isinstance(item, discord.ui.Button) and item.custom_id:
                    btn_acao = item.custom_id.split(":")[0].replace("ttk_", "")
                    if btn_acao in self.ttk_data[message_id]:
                        item.label = str(len(self.ttk_data[message_id][btn_acao]))

            await interaction.response.edit_message(view=view)
            await interaction.followup.send(msg_feedback, ephemeral=True)
            self.save_data()

            # Notifica o autor se for curtir, republicar ou salvar
            if is_new and author_id and author_id != user_id and tipo_acao in ["curtir", "republicar", "salvar"]:
                try:
                    autor = await self.bot.fetch_user(author_id)
                    if autor and not autor.bot:
                        if tipo_acao == "curtir":
                            acao_str = "curtiu"
                            emoji_str = self.config['emojis'].get('coracao', '💖')
                        elif tipo_acao == "republicar":
                            acao_str = "republicou"
                            emoji_str = self.config['emojis'].get('republicar', '🔁')
                        else:
                            acao_str = "salvou"
                            emoji_str = self.config['emojis'].get('salvar', '🔖')
                            
                        embed_dm = discord.Embed(
                            title="VOGUE - NOTIFICAÇÃO TIKTOK",
                            description=f"{emoji_str} **{interaction.user.display_name}** {acao_str} o seu vídeo!\n\n<:icon:1519007099948892381> **Nome:** {interaction.user.display_name}\n<:seta:1519006807014641874> **Username:** {interaction.user.name}\n<:info:1519007131012038737> **ID:** `{interaction.user.id}`",
                            color=int(self.config['colors']['sucesso'], 16) if isinstance(self.config['colors']['sucesso'], str) else self.config['colors']['sucesso']
                        )
                        await autor.send(embed=embed_dm)
                except:
                    pass

        elif tipo_acao == "apagar":
            if interaction.user.id == author_id or interaction.user.guild_permissions.administrator:
                if message_id in self.ttk_data:
                    del self.ttk_data[message_id]
                    self.save_data()
                await message.delete()
            else:
                await interaction.response.send_message(
                    f"{self.config['emojis'].get('erro', '❌')} Apenas o autor ou admin podem apagar.", 
                    ephemeral=True
                )

    @commands.command(name="ttk")
    @commands.has_any_role("ig", "IG", 1517365433714475170)
    async def ttk(self, ctx):
        """Comando de postagem para o TikTok."""
        emoji_ttk = self.config['emojis'].get('ttk', '📱')
        embed_prompt = discord.Embed(
            description=f"{emoji_ttk} **Envie o vídeo do TikTok em até 60 segundos!**",
            color=discord.Color(self.config['colors']['sucesso'])
        )
        msg_prompt = await ctx.send(embed=embed_prompt)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.attachments

        try:
            msg_user = await self.bot.wait_for('message', check=check, timeout=60.0)
            try:
                anexo = msg_user.attachments[0]
                ext = os.path.splitext(anexo.filename)[1].lower()
                
                # Bloqueia imagens, permite apenas vídeos
                if ext not in ['.mp4', '.mov', '.webm']:
                    await ctx.send(f"{self.config['emojis'].get('erro', '❌')} Por favor, envie apenas vídeos (.mp4, .mov, .webm).", delete_after=10)
                    return
                
                channel_id = self.config.get('channels', {}).get('tiktok')
                target_channel = self.bot.get_channel(channel_id)
                if not target_channel:
                    try:
                        target_channel = await self.bot.fetch_channel(channel_id)
                    except:
                        target_channel = ctx.channel
                
                # Configuração da View (Botões)
                view = discord.ui.View(timeout=None)
                author_safe_name = ctx.author.name.replace(":", "") # Evita quebrar o split
                
                emojis = self.config.get('emojis', {})
                view.add_item(discord.ui.Button(label="0", style=discord.ButtonStyle.secondary, custom_id=f"ttk_curtir:{ctx.author.id}:{author_safe_name}", emoji=emojis.get('coracao', '❤️')))
                view.add_item(discord.ui.Button(label="0", style=discord.ButtonStyle.secondary, custom_id=f"ttk_republicar:{ctx.author.id}:{author_safe_name}", emoji=emojis.get('republicar', '🔁')))
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.secondary, custom_id=f"ttk_comentar:{ctx.author.id}:{author_safe_name}", emoji=emojis.get('comentar', '💬')))
                view.add_item(discord.ui.Button(label="0", style=discord.ButtonStyle.secondary, custom_id=f"ttk_salvar:{ctx.author.id}:{author_safe_name}", emoji=emojis.get('salvar', '🔖')))
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.secondary, custom_id=f"ttk_apagar:{ctx.author.id}:{author_safe_name}", emoji=emojis.get('lixeira', '🗑️')))

                # Download do arquivo
                arquivo_midia = await anexo.to_file(filename=f"tiktok{ext}")
                
                # Conteúdo da mensagem (marcando o usuário)
                texto_post = f"{emoji_ttk} by **{ctx.author.display_name}** <@{ctx.author.id}>"

                # Procura ou cria Webhook para postar com o avatar do usuário
                webhooks = await target_channel.webhooks()
                webhook = discord.utils.get(webhooks, name="vogue-TikTok")
                if not webhook:
                    webhook = await target_channel.create_webhook(name="vogue-TikTok")

                await webhook.send(
                    content=texto_post,
                    file=arquivo_midia,
                    username=f"{ctx.author.display_name} • TikTok",
                    avatar_url=ctx.author.display_avatar.url,
                    view=view
                )

                # Limpeza Imediata de Setup
                try:
                    await ctx.message.delete()
                    await msg_prompt.delete()
                    await msg_user.delete()
                except:
                    pass

            except Exception as e:
                print(f"Erro ao processar vídeo: {e}")
                await ctx.send(f"{self.config['emojis'].get('erro', '❌')} Erro ao processar o vídeo.", delete_after=5)
                return

        except asyncio.TimeoutError:
            await msg_prompt.delete()
            await ctx.send(f"{self.config['emojis'].get('erro', '❌')} Tempo esgotado!", delete_after=5)

async def setup(bot):
    await bot.add_cog(TikTok(bot))
