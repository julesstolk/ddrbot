import json
import os
from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands

bot = discord.Bot()
bot = commands.Bot(command_prefix="=")
boardmessage = ""
playerselectoptions = [discord.SelectOption(label="Don't press please :D", description="Placeholder else the code'll break")]

def load(channel):
    with open(f"DDMatches/{str(channel)}.json") as f:
        return json.load(f)

def save(channel, gamesav):
    with open(f"DDMatches/{channel}.json", "w") as f:
        json.dump(gamesav, f)

def mktemp(player, P1, P2):
    if player == P1:
        return "P1"
    if player == P2:
        return "P2"

def makeBoardASCII(channel):
    game = load(channel)
    P1, P2 = str(channel).split("-")
    endrow = ""
    for i in range(1, 3):
        player = "P" + str(i)
        row = f"| HP {player}:{game['HP' + player]} | Hand:{len(game['hand' + player])} | Deck:{len(game['deck' + player])} | Magic:{game['magic' + player]} | Max Magic:{game['maxmagic' + player]} | Grave:{len(game['grave' + player])} | Banished:{len(game['banish' + player])} |"
        endrow += row + "\n"
        if i == 1:
            for j in range(1, 3):
                player2 = "P" + str(j)
                row = "| "
                for card in game["board" + player2]:
                    row += card + " | "
                row = row.strip()
                endrow += row + "\n"
    boardrows = list(endrow.split("\n"))
    longest = 0
    for row in boardrows:
        if len(row) > longest:
            longest = len(row)
    endrow = "```\n+" + "-" * (longest - 2) + "+\n" + endrow + "+" + "-" * (longest - 2) + "+```"
    return endrow

# boardcomps = [
#                 [
#                     Button(label = "See", style = 1, id = "see"), 
#                     Button(label = "Play", style = 1, id = "playcard"),
#                     Button(label = "Draw", style = 1, id = "drawcard"),
#                     Button(label = "Remove", style = 1, id = "removecard"),
#                     Button(label = "End Turn", style = 1, id = "end")
#                 ]
#             ]

class buttonBoard(discord.ui.View):
    global boardmessage
    @discord.ui.button(label="See", style=discord.ButtonStyle.primary)
    async def seesomething(self, button, interaction):
        await interaction.response.edit_message(view = seeBoard())

class seeBoard(discord.ui.View):
    @discord.ui.button(label="Hand", style=discord.ButtonStyle.primary)
    async def seehand(self, interaction):
        game = load(interaction.channel)
        P1, P2 = str(interaction.channel).split("-")
        temp = mktemp(str(interaction.user)[0:-5].lower(), P1, P2)
        await interaction.response.send_message(game['hand' + temp], ephemeral = True)

    @discord.ui.button(label="Deck", style=discord.ButtonStyle.primary)
    async def seedeck(self, interaction):
        game = load(interaction.channel)
        P1, P2 = interaction.channel.lower().split("-")
        temp = mktemp(str(interaction.user)[0:-5].lower(), P1, P2)
        await interaction.response.send_message(game['deck' + temp], ephemeral = True)

# class choosePlayers(discord.ui.View, playerselectoptions):
#     playerselectoptions = [discord.SelectOption(label="Don't press please :D", description="Placeholder else the code'll break")]
#     for item in openmatches:
#         playerselectoptions.append(discord.SelectOption(label=item))
    
#     @discord.ui.select(placeholder="Choose player", min_values=1, max_values=1, options = optionsselect())

#     async def select_callback(self, select, interaction):
#         playerselectoptions.remove(select.values[0])
#         newChannel = await interaction.create_text_channel(str(interaction.user)[0:-5] + str(select.values[0]), position = 5)
#         await interaction.response.edit_message(f"Created channel {newChannel}")

#     @discord.ui.button(label="Add myself", style=discord.ButtonStyle.primary)

#     async def button_callback(self, button, interaction):
#         openmatches.append(str(interaction.user)[0:-5])
#         await interaction.response.edit_message(content="Added you to the open matches list", view=None)

@bot.slash_command()
async def start(ctx):
    global boardmessage
    await ctx.respond(makeBoardASCII(ctx.channel), view = buttonBoard())


@bot.slash_command()
async def startmatch(ctx):
    class choosePlayers(discord.ui.View):
        
        @discord.ui.select(placeholder="Choose player", min_values=1, max_values=1, options = playerselectoptions)

        async def select_callback(self, select, interaction):
            for item in playerselectoptions:
                if item.label == select.values[0]:
                    playerselectoptions.remove(item)
                    matchplayer = str(item.label)
                    break
            newChannel = await discord.guild.create_text_channel(str(interaction.user)[0:-5] + matchplayer, category="784917482619404369", position = 5)
            await interaction.response.edit_message(f"Created channel {newChannel}")

        @discord.ui.button(label="Add myself", style=discord.ButtonStyle.primary)

        async def button_callback(self, button, interaction):
            playerselectoptions.append(discord.SelectOption(label=str(interaction.user)[0:-5]))
            await interaction.response.edit_message(content="Added you to the open matches list", view=None)
    
    await ctx.respond(f"These players want to play a match:", view = choosePlayers())


@bot.slash_command()
async def seecard(ctx, card):
    for item in os.listdir("assets/"):
        if card in item:
            await ctx.send(file=discord.File(f"Cards/{item}"))
            break
































bot.run("NzIxNDAzNzgzODY2NzQ0OTM1.GUsJE2.-6T6MHzfWGirEEsle5YBkWVS6jeYWn_u5r7Di8")