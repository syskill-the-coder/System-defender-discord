from pydoc import describe
from simplelogging import *
config("systemdefender.log", True)
log("Loading modules", "INFO")
import discord
from discord.ext import commands, tasks
from colorama import Fore, init
from discord import Permissions
import traceback
from discord_webhook import DiscordWebhook
log("Loading asyncio...", "INFO")
import asyncio
log("Defining variables, classes and functions...","INFO")
import keepalive

version = "SysDef DEV 0.0"
token = "OTg0NDcwMzUxOTE0MzQwNDEz.GjrwQb.BaEzC3BBp0AIKUTNuSm99Cq7sSy475EfKiEkcs"
channeltoggle = False
spam_count = {}
spam_count_reset_sec = 10
spam_count_last_reset = 0
spam_cap = 3 #spam_cap messages every spam_count_reset_sec
muted = []
txt_icon = """
 .d8888b.                 888                         
d88P  Y88b                888                         
Y88b.                     888                         
 "Y888b.  888  888.d8888b 888888 .d88b. 88888b.d88b.  
    "Y88b.888  88888K     888   d8P  Y8b888 "888 "88b 
      "888888  888"Y8888b.888   88888888888  888  888 
Y88b  d88PY88b 888     X88Y88b. Y8b.    888  888  888 
 "Y8888P"  "Y88888 88888P' "Y888 "Y8888 888  888  888 
               888                                    
          Y8b d88P                                    
           "Y88P"                                     

8888888b.          .d888                     888                
888  "Y88b        d88P"                      888                
888    888        888                        888                
888    888 .d88b. 888888 .d88b. 88888b.  .d88888 .d88b. 888d888 
888    888d8P  Y8b888   d8P  Y8b888 "88bd88" 888d8P  Y8b888P"   
888    88888888888888   88888888888  888888  88888888888888     
888  .d88PY8b.    888   Y8b.    888  888Y88b 888Y8b.    888     
8888888P"  "Y8888 888    "Y8888 888  888 "Y88888 "Y8888 888     
"""


bot = commands.Bot(command_prefix = "?", intents=discord.Intents.all())




class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '' \
               '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title=f"Help for {version}:")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Default Commands:")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)


        channel = self.context.author
        await channel.send(embed=embed)

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Error", description=str(error))
            await ctx.send(embed=embed)
        else:
            raise error

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome to {member.guild.name} {member.mention}!')

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member



bot.help_command = MyHelp()
init(convert=True)
bot.add_cog(Greetings(bot))

@bot.event
async def on_ready():
    log(f"{Fore.GREEN} {txt_icon}\n"
          f"Is online.", "INFO")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name="?help"), status=discord.Status.do_not_disturb)
    keepalive.keep_alive()
    while True:
        log("Cleared spam file", "DEBUG")
        await asyncio.sleep(spam_count_reset_sec)
        with open("spammers.txt", "r+") as file:
            file.truncate(0)
    


@bot.event
async def on_guild_channel_create(channel):
    embed = discord.Embed(title="Server :white_check_mark:", description="This server is protected by\n"
                                                      "System Defender, made by The_SysKill.\n"
                                                      "To toggle these messages, type ?channel_toggle.")
    if channeltoggle:
        await channel.send(embed=embed)

@bot.event
async def on_guild_join(guild):
    print(f"{Fore.GREEN}Joined guild {guild.name}.")

@bot.event
async def on_guild_remove(guild):
    print(f"{Fore.RED}Left guild {guild.name}")

@bot.event
async def on_member_ban(guild,member):
    print(f"{Fore.RED}{member.name}#{member.discriminator} was banned from {guild.name}.")

@bot.event
async def on_member_unban(guild, member):
    print(f"{Fore.GREEN}{member.name}#{member.discriminator} was unbanned from {guild.name}.")

@bot.event
async def on_member_join(member):
    print(f"{Fore.GREEN}{member.name}#{member.discriminator} Joined a mutual guild.")

@bot.event
async def on_member_remove(member):
    print(f"{Fore.RED}{member.name}#{member.discriminator} Left a mutual guild")

@bot.command(help="Toggles the messages when new channels are created")
async def channel_toggle(ctx):
    global channeltoggle
    channeltoggle = not channeltoggle
    await ctx.send(embed=discord.Embed(title="Toggle", description=f"New channel messages is now set to {channeltoggle}"))

@bot.command()
async def shutup(ctx):
  if str(ctx.message.author) == "†hê_§¥§Kïll#1878":
    await ctx.send("Ok, imma stfu")
    await bot.change_presence(status=discord.Status.offline)
    await bot.logout()

@bot.command()
async def msg(ctx, target:discord.Member, *, message):
    dm = await target.create_dm()
    embed = discord.Embed(title="Message", description=f"You received a message from guild {ctx.guild.name},\n"
                                                       f"This was sent by <@!{ctx.message.author.id}>.", color=0xffff00)
    embed.add_field(name="Message:", value=message.replace("\\n", "\n"))
    try:
        await dm.send(embed=embed)
        await ctx.reply(":white_check_mark:")
    except:
        embed = discord.Embed(title="Error",description=f"Failed to dm {target.display_name}." ,color=0xff0000)
        await ctx.send(embed=embed)
@msg.error
async def error(ctx, error):
    if isinstance(error, discord.ext.commands.MemberNotFound):
        await ctx.reply(embed=discord.Embed(title="Message", description="I could not find that user.", color=0xff000f))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply(embed = discord.Embed(title="Message", description="Permission denied. **Manage Messages** Permission required.", color=0xff000f))
@bot.command()
async def is_mobile(ctx, target:discord.Member):
    if target.is_on_mobile():
        await ctx.send("True")
    else:
        await ctx.send("False")



@bot.command()
async def role_higher_than(ctx, target:discord.Member, silent = False):
    if max(ctx.message.author.roles) > max(target.roles):
        if not silent:
            await ctx.send(f"You have more hierarchy than {target.display_name}.")
        return True
    else:
        if not silent:
            await ctx.send(f"You have less or equal hierarchy than {target.display_name}.")
        return False

@bot.command(description="Unmutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
   await member.remove_roles(mutedRole)
   await ctx.message.reply(f"Unmuted {member.display_name}")


@bot.command(description="Mutes a specified user.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member,minutes:int=15 ,  *, reason="No reason specified"):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(mutedRole)
    await ctx.message.reply(f"Muted {member.display_name}")
    global muted
    muted.append(str(member.mention))
    await asyncio.sleep(minutes*60)
    muted.remove(str(member.mention))
    await ctx.send(f"?unmute {member.mention}")
    await member.remove_roles(mutedRole)

@bot.command(help="Legacy ban.")
@commands.has_permissions(administrator=True)
async def hardban(ctx, target:discord.Member,*,reason="No reason specified."):
    await target.ban(reason=reason)
    await ctx.send(f"> {target.display_name} Was **HARD-BANNED** by admin {ctx.message.author}!!!\n"
                   f"> Reason: {reason}.")

@hardban.error
async def hardban_error(error, ctx):
    if isinstance(error, commands.MissingPermissions):
        text = "Sorry {}, you do not have permissions to do that!\n" \
               "The minimal required permissions for this command are:\n" \
               "**Administrator**".format(ctx.message.author)
        await bot.send_message(ctx.message.channel, text)


@bot.command()
async def dev_error(ctx):
    assert 5 > 6

@bot.event
async def on_message(message):
    if "$SUDO" in message.content.upper():
      await message.reply("U are not a hacker lol. SysKill is :sunglasses:")
    await bot.process_commands(message)
    print(f"{str(message.author)}\n"
          f"{muted}")
    if discord.utils.get(message.guild.roles, name="Muted") in message.author.roles:
        if message.author.guild_permissions.manage_messages:
            return
        await message.delete()
        return
    counter = 0


    with open("spammers.txt", "r+") as file:
        for lines in file:
            if lines.strip("\n") == str(message.author.id):
                counter += 1
        file.writelines(f"{str(message.author.id)}\n")
    if counter > spam_cap:
        await message.delete()
        await message.channel.send(f"User <@!{message.author.id}> Was flagged for spamming!")
        await message.author.add_roles(discord.utils.get(message.guild.roles, name="Muted"))
        await asyncio.sleep(3*60)
        await message.author.remove_roles(discord.utils.get(message.guild.roles, name="Muted"))
        await message.channel.send(f"User <@!{message.author.id}> Was unmuted")
    if "REACT TO THIS MESSAGE" in message.content.upper():
        await message.add_reaction("👍")

@bot.event
async def on_error(event, args=None, kwargs=None):
    message = args[0]  # Gets the message object
    log("Unknown Event raised on_error, traceback:\n"+traceback.format_exc(), "ERROR")  # logs the error

@bot.event
async def on_command_error(ctx, error):
    log(f"Unknown Event raised on_command_error, Check Console.\n \
        Faulty command: |{ctx.message.content}|", "WARNING")

try:
    bot.run(token)
except:
    log("Fatal error during login:\n"+traceback.format_exc(), "LOGIN_FATAL")