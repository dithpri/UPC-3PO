#@app_commands.guilds(test_server)

#TODO: WA Ping Listener & start/stop command, NNE Dispatch, Join WA Dispatch
import datetime
import discord
import os
import re

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from dotenv import load_dotenv

from the_brain import api_call, format_names

load_dotenv()
ID = int(os.getenv("ID"))

class balder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.wa_listener.is_running():
            self.wa_listener.start()
    '''

    #Checks
    def isTestServer():
        async def predicate(ctx):
            return ctx.guild.id == 1022638031838134312
        return commands.check(predicate)

    def isUPC():
        async def predicate(ctx):
            return ctx.message.author.id == ID
        return commands.check(predicate)

#===================================================================================================#
    @tasks.loop(hours=1)
    async def wa_listener(self):
        maintenance_channel = self.bot.get_channel(1022638032295297124)

        f = open("logs\watchers.txt", "r")
        watchers = [watcher for watcher in f.read().split(",")]
        f.close()

        notices_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=UPCY&q=notices", mode=2).text, "xml")

        for notice in notices_data.find_all("NOTICE"):
            if notice.find("NEW") and notice.TYPE.text == "RMB" and re.search("(?<==).+?(?=/)", notice.URL.text).group(0) == "hesperides":
                message_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region=hesperides&q=messages;limit=1;id={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}", mode=1).text, "xml")

                nation = message_data.NATION.text
                message_text = re.search('(?<=\[/nation\]).+', message_data.MESSAGE.text).group(0)

                if "in" in message_text and nation not in watchers:
                    watchers.append(nation)
                elif "out" in message_text and nation in watchers:
                    watchers.remove(nation)

        f = open("logs\watchers.txt", "w")
        f.write(",".join(watchers))
        f.close()

        timestamp = int(datetime.datetime.now().timestamp())
        message = await maintenance_channel.fetch_message(1023257199327330344)
        embed_data = message.embeds[0].to_dict()
        embed_data['fields'][0]["value"] = f'<t:{timestamp}:f> -- <t:{timestamp}:R>'
        embed = discord.Embed.from_dict(embed_data)
        await message.edit(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="wa_listener_setup", with_app_command=True, description="Run this command to create the initial embed for the Balder WA Program")
    @isUPC()
    async def wa_listener_setup(self, ctx:commands.Context):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Balder World Assembly Automation Status", color=color)
        embed.add_field(name="WA Ping Listener", value="None", inline=False)
        embed.add_field(name="NNE Dispatch", value="None", inline=False)
        embed.add_field(name="Join the WA Dispatch", value="None", inline=False)
        await ctx.reply(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="listener", with_app_command=True, description="Start or stop the listener")
    @commands.has_permissions(administrator=True)
    @isTestServer()
    @app_commands.choices(
        action = [
            Choice(name="start", value="start"),
            Choice(name="stop", value="stop")
        ]
    )
    async def listener(self, ctx:commands.Context, action: str):
        await ctx.defer()

        match action:
            case "start":
                if not self.wa_listener.is_running():
                    self.wa_listener.start()
                    await ctx.reply("Listener started.")
                else:
                    await ctx.reply("Listener is already running.")
            case "stop":
                if self.wa_listener.is_running():
                    self.wa_listener.cancel()
                    await ctx.reply("Listener stopped.")
                else:
                    await ctx.reply("Listener already stopped.")
#===================================================================================================#
async def setup(bot):
    await bot.add_cog(balder(bot))