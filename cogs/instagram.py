import discord
from discord.ext import commands
import asyncio
import json
import os
import io
from PIL import Image

class Instagram(commands.Cog):
    """Módulo Instagram Híbrido - Otimizado para Resposta Imediata e Persistência."""
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.likes_path = os.path.join(os.path.dirname(__file__), "likes.json")
        self.likes_data = self.load_likes()

    def load_likes(self):
        """Carrega as curtidas do arquivo JSON."""
        if os.path.exists(self.likes_path):
            try:
                with open(self.likes_path, "r") as f:
                    data = json.load(f)
                    return {str(msg_id): set(users) for msg_id, users in data.items()}
            except Exception:
                return {}
        return {}

    def save_likes(self):
        """Salva as curtidas no arquivo JSON."""
        try:
            data = {str(msg_id): list(users) for msg_id, users in self.likes_data.items()}
            with open(self.likes_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro ao salvar likes.json: {e}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Gerencia interações via botões com prioridade de resposta para evitar timeouts."""
        custom_id = interaction.data.get('custom_id')
        if not custom_id or not custom_id.startswith("insta_"):
            return

        # 1. Extração rápida de dados
        author_id = None
        try:
            if ":" in custom_id:
                parts = custom_id.split(":")
                acao = parts[0]
                author_id = int(parts[1])
            else:
                acao = custom_id
                if interaction.message.embeds:
                    footer = interaction.message.embeds[0].footer.text
                    if "ID: " in footer:
                        author_id = int(footer.split("ID: ")[1])
        except:
            pass

        message = interaction.message
        message_id = str(message.id)
        user_id = interaction.user.id

        # --- LÓGICA DE CURTIR ---
        if acao.startswith("insta_curtir"):
            if message_id not in self.likes_data:
                self.likes_data[message_id] = set()

            # Lógica de Like/Unlike rápida
            is_new_like = False
            if user_id in self.likes_data[message_id]:
                self.likes_data[message_id].remove(user_id)
                msg_feedback = "Você removeu sua curtida."
            else:
                self.likes_data[message_id].add(user_id)
                msg_feedback = "Você curtiu esta postagem!"
                is_new_like = True

            # --- RESPOSTA IMEDIATA (CRÍTICO PARA EVITAR TIMEOUT) ---
            # Atualiza o botão primeiro para o usuário sentir a resposta instantânea
            view = discord.ui.View.from_message(message)
            for item in view.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == custom_id:
                    item.label = str(len(self.likes_data[message_id]))
            
            # Reconhece a interação editando a mensagem (Dessa forma o Discord não dá erro 404)
            await interaction.response.edit_message(view=view)
            
            # Envia o feedback efêmero usando followup (para não bloquear a resposta anterior)
            await interaction.followup.send(msg_feedback, ephemeral=True)

            # --- TAREFAS DE FUNDO (Lentas) ---
            # Salva no disco após responder ao Discord
            self.save_likes()

            # Notificação via DM se for um novo Like
            if is_new_like and author_id:
                try:
                    autor = await self.bot.fetch_user(author_id)
                    if autor and not autor.bot:
                        embed_dm = discord.Embed(
                            title="VOGUE - NOTIFICAÇÃO",
                            description=f"💖 **{interaction.user.display_name}** curtiu sua postagem!\n\n<:icon:1519007099948892381> **Nome:** {interaction.user.display_name}\n<:seta:1519006807014641874> **Username:** {interaction.user.name}\n<:info:1519007131012038737> **ID:** `{interaction.user.id}`",
                            color=int(self.config['colors']['sucesso'], 16) if isinstance(self.config['colors']['sucesso'], str) else self.config['colors']['sucesso']
                        )
                        embed_dm.set_footer(text="vogue • Estética & Segurança")
                        await autor.send(embed=embed_dm)
                except:
                    pass

        # --- LÓGICA DE APAGAR ---
        elif acao.startswith("insta_apagar"):
            if interaction.user.id == author_id or interaction.user.guild_permissions.administrator:
                if message_id in self.likes_data:
                    del self.likes_data[message_id]
                    self.save_likes()
                await message.delete()
            else:
                await interaction.response.send_message(
                    f"{self.config['emojis']['erro']} Apenas o autor ou admin podem apagar.", 
                    ephemeral=True
                )

    @commands.command(name="insta")
    @commands.has_any_role("ig", "IG", 1517365433714475170)
    async def insta(self, ctx):
        """Comando de postagem unificada."""
        embed_prompt = discord.Embed(
            description=f"{self.config['emojis']['insta']} **Envie a imagem (com ou sem legenda) em até 60 segundos!**",
            color=discord.Color(self.config['colors']['sucesso'])
        )
        msg_prompt = await ctx.send(embed=embed_prompt)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.attachments

        try:
            msg_user = await self.bot.wait_for('message', check=check, timeout=60.0)
            try:
                anexo = msg_user.attachments[0]
                legenda = msg_user.content if msg_user.content.strip() else None
                ext = os.path.splitext(anexo.filename)[1].lower()
                
                channel_id = self.config.get('channels', {}).get('instagram')
                target_channel = self.bot.get_channel(channel_id)
                if not target_channel:
                    try:
                        target_channel = await self.bot.fetch_channel(channel_id)
                    except:
                        target_channel = ctx.channel
                
                # Procura ou cria Webhook para renderização superior
                webhooks = await target_channel.webhooks()
                webhook = discord.utils.get(webhooks, name="vogue-Instagram")
                if not webhook:
                    webhook = await target_channel.create_webhook(name="vogue-Instagram")

                # Configuração da View (Persistente via Custom ID)
                view = discord.ui.View(timeout=None)
                view.add_item(discord.ui.Button(label="0", style=discord.ButtonStyle.secondary, custom_id=f"insta_curtir:{ctx.author.id}", emoji=self.config['emojis']['coracao']))
                view.add_item(discord.ui.Button(style=discord.ButtonStyle.secondary, custom_id=f"insta_apagar:{ctx.author.id}", emoji=self.config['emojis']['lixeira']))

                # Preparação do Arquivo e Padronização de Tamanho
                try:
                    if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
                        await ctx.send(f"{self.config['emojis']['erro']} Por favor, envie apenas imagens (.png, .jpg, .webp). Vídeos não são suportados aqui.", delete_after=10)
                        return
                    
                    image_bytes = await anexo.read()
                    img = Image.open(io.BytesIO(image_bytes))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    width, height = img.size
                    aspect_ratio = 4 / 5
                    target_width = width
                    target_height = int(target_width / aspect_ratio)
                    
                    if target_height > height:
                        target_height = height
                        target_width = int(target_height * aspect_ratio)
                        
                    left = int((width - target_width) / 2)
                    top = int((height - target_height) / 2)
                    right = int((width + target_width) / 2)
                    bottom = int((height + target_height) / 2)
                    
                    img_cropped = img.crop((left, top, right, bottom))
                    # Redimensiona para o tamanho padrão do Instagram (Vertical)
                    img_cropped = img_cropped.resize((1080, 1350), Image.Resampling.LANCZOS)
                    
                    output = io.BytesIO()
                    img_cropped.save(output, format='PNG')
                    output.seek(0)
                    
                    arquivo_midia = discord.File(fp=output, filename="post.png")
                    ext = ".png"
                except Exception as e:
                    await ctx.send(f"{self.config['emojis']['erro']} Erro ao processar arquivo: `{str(e)}`", delete_after=15)
                    print(e)
                    return
                
                cor = int(self.config['colors']['sucesso'], 16) if isinstance(self.config['colors']['sucesso'], str) else self.config['colors']['sucesso']
                
                embed = discord.Embed(
                    description=legenda,
                    color=cor
                )
                embed.set_author(name=f"{ctx.author.name} • Instagram", icon_url=ctx.author.display_avatar.url)
                embed.set_image(url="attachment://post.png")
                
                await webhook.send(
                    file=arquivo_midia,
                    embed=embed,
                    username=f"{ctx.author.display_name} • Instagram",
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
                print(f"Erro ao processar postagem: {e}")
                await ctx.send(f"{self.config['emojis']['erro']} Erro ao processar arquivo.", delete_after=5)
                return


        except asyncio.TimeoutError:
            await msg_prompt.delete()
            await ctx.send(f"{self.config['emojis']['erro']} Tempo esgotado!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Instagram(bot))
