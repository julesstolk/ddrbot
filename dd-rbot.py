import json
import os
from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands
import random
bot = discord.Bot()
bot = commands.Bot(command_prefix="=")
playerselectoptions = [discord.SelectOption(label="Don't press please :D", description="Placeholder else the code'll break")]
game = {}
samplegamesave = {
    "hp": 20, 
    "board": [], 
    "hand": [], 
    "deck": [], 
    "magic": 0, 
    "maxmagic": 0, 
    "grave": [], 
    "banish": []
}

def load(channel):
    with open(f"DDMatches/{str(channel)}.json") as f:
        return json.load(f)

def save(channel, game):
    with open(f"DDMatches/{channel}.json", "w") as f:
        json.dump(game, f)

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
        row = f"| HP {player}:{game['hp' + player]} | Hand:{len(game['hand' + player])} | Deck:{len(game['deck' + player])} | Magic:{game['magic' + player]} | Max Magic:{game['maxmagic' + player]} | Grave:{len(game['grave' + player])} | Banished:{len(game['banish' + player])} |"
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
    @discord.ui.button(label="See", style=discord.ButtonStyle.primary)

    async def seesomething(self, button, interaction):
        await interaction.response.edit_message(view = seeBoard())

    @discord.ui.button(label="Play", style=discord.ButtonStyle.primary)

    async def play_callback:
        await interaction.response.edit_message(view = playCard())

    @discord.ui.button(label="Draw", style=discord.ButtonStyle.primary)

    async def draw_callback:
        player = str(interaction.user)[0:-5]
        drawncard = random.choice(game["deck" + player])
        game["deck" + player].remove(drawncard)
        game["hand" + player].append(drawncard)
        await interaction.response.send_message(content=f"You've drawn ``{drawncard}``", ephemeral=True)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))

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


        await interaction.response.send_message(game['deck' + str(interaction.user)[0:-5]], ephemeral = True)


@bot.slash_command()
async def start(ctx):
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
                    otherplayer = str(interaction.user[0:-5])
                    break
            newChannel = await interaction.guild.create_text_channel("`" + otherplayer + "-" + matchplayer + "`", category=interaction.channel.category, position = 9)
            await interaction.response.edit_message(content=f"Created channel {newChannel}")
            with open(f"games\\{otherplayer}-{matchplayer}.json") as f:
                newgamesave = {}
                for key in samplegamesave:
                    newgamesave[key + otherplayer] = samplegamesave[key]
                    newgamesave[key + matchplayer] = samplegamesave[key]
                json.dump(newgamesave, f)
                

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
