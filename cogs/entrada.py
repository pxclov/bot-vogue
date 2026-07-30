import discord
from discord.ext import commands

class Entrada(commands.Cog):
    """Módulo responsável pelas ações quando um novo membro entra no servidor."""
    def __init__(self, bot):
        self.bot = bot
        # ID do cargo "Vogue" que será entregue automaticamente
        self.cargo_vogue_id = 1516976401893294100
        # ID do cargo que funciona como exceção (não deve receber o auto-role)
        self.cargo_excecao_id = 1516992437023674408

    @commands.Cog.listener()
    async def on_ready(self):
        """Verifica se existem membros sem o cargo de verificação ao ligar o bot."""
        print("[Auto-Role] Iniciando verificação de membros sem cargo...")
        for guild in self.bot.guilds:
            cargo = guild.get_role(self.cargo_vogue_id)
            if not cargo:
                continue
            
            adicionados = 0
            for member in guild.members:
                # Se for bot, ou se já tem o cargo vogue, ou se tem o cargo de exceção, ignora.
                if member.bot or cargo in member.roles or any(r.id == self.cargo_excecao_id for r in member.roles):
                    continue
                
                try:
                    await member.add_roles(cargo, reason="Sincronização de Cargo Vogue ao ligar o bot")
                    adicionados += 1
                except discord.Forbidden:
                    pass # Ignora silenciosamente se não tiver permissão
                except Exception:
                    pass
            
            if adicionados > 0:
                print(f" [Auto-Role] Sincronização concluída em '{guild.name}': {adicionados} membros receberam o cargo.")
            else:
                print(f" [Auto-Role] Sincronização concluída em '{guild.name}': Todos já possuem o cargo (ou têm a exceção).")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Evento acionado quando um usuário entra no servidor."""
        try:
            cargo = member.guild.get_role(self.cargo_vogue_id)
            if cargo:
                await member.add_roles(cargo, reason="Cargo Vogue adicionado automaticamente ao entrar no servidor")
                print(f" [Auto-Role] O cargo Vogue foi dado com sucesso para {member.name}.")
            else:
                print(f"[Auto-Role] Cargo Vogue (ID: {self.cargo_vogue_id}) não foi encontrado no servidor.")
        except discord.Forbidden:
            print(f" [Auto-Role] Permissão negada! O bot precisa estar ACIMA do cargo Vogue na hierarquia para poder entregá-lo (e ter a permissão de Gerenciar Cargos).")
        except Exception as e:
            print(f" [Auto-Role] Erro ao adicionar cargo ao membro {member.name}: {e}")

async def setup(bot):
    await bot.add_cog(Entrada(bot))
