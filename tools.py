import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class DiscordTools(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=discord.Intents.all())
        
    async def on_ready(self):
        print(f"[{self.user.name}] Araç Seti Modülü Aktif.")
        await self.change_presence(activity=discord.Game(name="Araçlar Enes tarafından hazırlanmıştır."))

    def embed_tasarim(self, title, desc, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text="Enes tarafından yapılmıştır")
        return embed

bot = DiscordTools()


@bot.command(name="temizle", aliases=["sil", "purge"])
@commands.has_permissions(manage_messages=True)
async def temizle(ctx, miktar: int):
    """Belirtilen miktarda mesajı tek seferde siler."""
    await ctx.message.delete()
    silinen = await ctx.channel.purge(limit=miktar)
    msg = await ctx.send(embed=bot.embed_tasarim("🧹 Temizlik Yapıldı", f"Kanaldan başarıyla **{len(silinen)}** mesaj temizlendi.", discord.Color.green()))
    await msg.delete(delay=5)

@bot.command(name="roldagit", aliases=["roleall"])
@commands.has_permissions(manage_roles=True)
async def roldagit(ctx, rol: discord.Role):
    """Sunucudaki tüm üyelere belirtilen rolü verir (Botları hariç tutar)."""
    await ctx.send(embed=bot.embed_tasarim("⏳ İşlem Başlatıldı", f"**{rol.name}** rolü tüm üyelere dağıtılıyor... Sunucu boyutuna göre zaman alabilir."))
    
    sayac = 0
    for member in ctx.guild.members:
        if not member.bot and rol not in member.roles:
            try:
                await member.add_roles(role)
                sayac += 1
            except discord.Forbidden:
                return await ctx.send("[HATA] Botun rol yetkisi bu işlemi yapmak için yetersiz.")
                
    await ctx.send(embed=bot.embed_tasarim("✅ İşlem Tamamlandı", f"Toplam **{sayac}** üyeye başarıyla {rol.mention} rolü verildi.", discord.Color.green()))

@bot.command(name="sunucubilgi", aliases=["serverinfo"])
async def sunucubilgi(ctx):
    """Sunucunun detaylı teknik verilerini listeler."""
    guild = ctx.guild
    desc = (
        f"**Sunucu Adı:** {guild.name}\n"
        f"**Kurucu:** {guild.owner.mention} ({guild.owner_id})\n"
        f"**Üye Sayısı:** {guild.member_count}\n"
        f"**Rol Sayısı:** {len(guild.roles)}\n"
        f"**Kanal Sayısı:** {len(guild.channels)} (Kategori: {len(guild.categories)})\n"
        f"**Takviye Seviyesi:** {guild.premium_tier}. Seviye ({guild.premium_subscription_count} Takviye)"
    )
    await ctx.send(embed=bot.embed_tasarim(f"📊 {guild.name} - Sunucu Bilgileri", desc))

@bot.command(name="davetler")
@commands.has_permissions(manage_guild=True)
async def davetler(ctx):
    """Sunucudaki aktif davet linklerini ve kullanım sayılarını listeler."""
    try:
        guild_invites = await ctx.guild.invites()
    except discord.Forbidden:
        return await ctx.send("[HATA] Davetleri görmek için 'Sunucuyu Yönet' yetkim olmalı.")

    if not guild_invites:
        return await ctx.send("Sunucuda oluşturulmuş aktif bir davet linki bulunmuyor.")

    liste = ""
    for invite in guild_invites[:10]:
        liste += f"🔗 `{invite.code}` - **Oluşturan:** {invite.inviter.name} - **Kullanım:** `{invite.uses}`\n"

    await ctx.send(embed=bot.embed_tasarim("📩 Aktif Davet Linkleri (Top 10)", liste))

@bot.command(name="rolsuzver")
@commands.has_permissions(manage_roles=True)
async def rolsuzver(ctx, rol: discord.Role):
    """Sunucuda hiçbir rolü olmayan üyelere toplu şekilde belirtilen rolü verir."""
    await ctx.send(embed=bot.embed_tasarim("⏳ Tarama Başladı", "Sunucudaki rolü olmayan üyeler taranıyor..."))
    
    sayac = 0
    for member in ctx.guild.members:
        if len(member.roles) == 1 and not member.bot:
            await member.add_roles(role)
            sayac += 1
            
    await ctx.send(embed=bot.embed_tasarim("✅ İşlem Tamamlandı", f"Hiçbir rolü bulunmayan **{sayac}** üyeye {rol.mention} rolü tanımlandı.", discord.Color.green()))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için gerekli yetkiye sahip değilsin.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Eksik argüman girdin. Doğru kullanım: `{ctx.prefix}{ctx.command.name} [parametre]`")

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("[HATA] .env dosyasında TOKEN eksik.")
