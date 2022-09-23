from code import interact
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
    "board": ["--+--", "--+--", "--+--", "--+--", "--+--"], 
    "hand": [], 
    "deck": [], 
    "magic": 0, 
    "maxmagic": 0, 
    "grave": [], 
    "banish": []
}

def load(channel):
    with open(f"games/{str(channel)}.json") as f:
        return json.load(f)

def save(channel, game):
    with open(f"games/{str(channel)}.json", "w") as f:
        json.dump(game, f)

def makeBoardASCII(channel):
    p1, p2 = str(channel).split("-")
    game = load(channel)
    boardlist1, boardlist2 = game["board" + p1], game["board" + p2]
    while len(boardlist1) != 5:
        boardlist1.append("--+--")
    while len(boardlist2) != 5:
        boardlist2.append("--+--")
    boardlists = [boardlist1, boardlist2]
    game = load(channel)
    endrow = ""
    playerlist = list(str(channel).split("-"))
    for i in range(0, 2):
        player = playerlist[i]
        row = f"|HP {player}:{game['hp' + player]}|Hand:{len(game['hand' + player])}|Deck:{len(game['deck' + player])}|Magic:{game['magic' + player]}|Max Magic:{game['maxmagic' + player]}|Grave:{len(game['grave' + player])}|Banish:{len(game['banish' + player])}|"
        endrow += row + "\n"
        if i == 0:
            for j in range(0, 2):
                row = "| | "
                for card in boardlists[j]:
                    row += card + " | "
                row = row + " |"
                endrow += row + "\n"
    boardrows = list(endrow.split("\n"))
    longest = 0
    for row in boardrows:
        if len(row) > longest:
            longest = len(row)
    endrow = "```\n+" + "-" * (longest - 2) + "+\n" + endrow + "+" + "-" * (longest - 2) + "+```"
    return endrow

class buttonBoard(discord.ui.View):

    @discord.ui.button(label="See", style=discord.ButtonStyle.primary)
    async def see_callback(self, button, interaction):
        await interaction.response.edit_message(view = seeBoard())

    @discord.ui.button(label="Play", style=discord.ButtonStyle.primary)
    async def play_callback(self, button, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        playstring, i = "", 1
        for item in game["hand" + player]:
            playstring += item + ", "
        playstring = playstring [0:-2]

        class playCardModal(discord.ui.Modal):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.add_item(discord.ui.InputText(label=playstring))

            async def callback(self, interaction):
                game = load(interaction.channel)
                player = str(interaction.user)[0:-5].lower()
                card = self.children[0].value
                game["hand" + player].remove(card)
                for i in range(len(game["board" + player])):
                    if game["board" + player][i] == "--+--":
                        game["board" + player][i] = card
                        save(interaction.channel, game)
                        print("uh")
                        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())
                        return
                await interaction.response.send_message(content="That is not a valid card index.", ephemeral=True)
    
        playModal = playCardModal(title="Play a card")
        await interaction.response.send_modal(playModal)
        
    @discord.ui.button(label="Remove", style=discord.ButtonStyle.primary)
    async def remove_callback(self, button, interaction):
        game = load(interaction.channel)
        p1, p2 = str(interaction.channel).split("-")

        class removeSelectCard(discord.ui.View):
            @discord.ui.button(label=game["board" + p1], style=discord.ButtonStyle.primary)
            async def remove_callback1(self, button, interaction):
                pass 

    @discord.ui.button(label="Draw", style=discord.ButtonStyle.primary)
    async def draw_callback(self, button, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        drawncard = random.choice(game["deck" + player])
        game["deck" + player].remove(drawncard)
        game["hand" + player].append(drawncard)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))

    @discord.ui.button(label="Deck", style=discord.ButtonStyle.primary)
    async def deck_callback(self, button, interaction):
        await interaction.response.edit_message(view=editDeck())

    @discord.ui.button(label="End Turn", style=discord.ButtonStyle.danger)
    async def endturn_callback(self, button, interaction):
        pass



class seeBoard(discord.ui.View):
    @discord.ui.button(label="Hand", style=discord.ButtonStyle.primary)
    async def seehand(self, button, interaction):
        game = load(interaction.channel)
        await interaction.response.send_message(game['hand' + str(interaction.user)[0:-5].lower()], ephemeral = True)

    @discord.ui.button(label="Deck", style=discord.ButtonStyle.primary)
    async def seedeck(self, button, interaction):
        game = load(interaction.channel)
        await interaction.response.send_message(game['deck' + str(interaction.user)[0:-5].lower()], ephemeral = True)
        
    @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
    async def escape_callback(self, button, interaction):
        await interaction.response.edit_message(view=buttonBoard())

class addDeckModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Type the card you want to add."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        game["deck" + str(interaction.user)[0:-5].lower()].append(self.children[0].value)
        save(interaction.channel, game)
        await interaction.response.send_message(content=f"Added card '{str(self.children[0].value)}' to your deck.", ephemeral=True)

class editDeck(discord.ui.View):
    @discord.ui.button(label="Add to deck", style=discord.ButtonStyle.primary)
    async def add_to_deck_callback(self, button, interaction):
        deckModal = addDeckModal(title="Add to deck")
        await interaction.response.send_modal(deckModal)
        
    @discord.ui.button(label="Use deck", style=discord.ButtonStyle.primary)
    async def use_deck_callback(self, button, interaction):

        loadDecks = {}
        with open("decks.json", "r") as f:
            loadDecks = json.load(f)

        loadedDeckList = []
        
        for item in loadDecks.keys():
            loadedDeckList.append(discord.SelectOption(label=item))

        class useDeck(discord.ui.View):
            @discord.ui.select(placeholder="Select your deck:", min_values=1, max_values=1, options=loadedDeckList)
        
            async def deck_choice_callback(self, select, interaction):
                game = load(interaction.channel)
                player = str(interaction.user)[0:-5].lower()
                game["deck" + player].extend(loadDecks[select.values[0]])
                save(interaction.channel, game)
                await interaction.response.send_message(content=f"Added premade deck '{select.values[0]}' to your deck.", ephemeral=True)

            @discord.ui.button(label="Escape", style=discord.ButtonStyle.primary)
            
            async def escape_button(self, button, interaction):
                await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())
        await interaction.response.edit_message(view=useDeck())

    @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
    async def escape_callback(self, button, interaction):
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())
    
class chooseRemove(discord.ui.View):
    @discord.ui.button(label="Grave", style=discord.ButtonStyle.primary)
    async def moveGrave(self, button, interaction):
        pass

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
                    matchplayer = str(item.label).lower()
                    otherplayer = str(interaction.user)[0:-5].lower()
                    break
            newChannel = await interaction.guild.create_text_channel("`" + matchplayer + "-" + otherplayer + "`", category=interaction.channel.category, position = 9)
            await interaction.response.edit_message(content=f"Created channel {newChannel}")
            with open(f"games/{matchplayer}-{otherplayer}.json", "w") as f:
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


@bot.slash_command()
async def add_deck(ctx, name: str, deck):
    deck = list(deck.split(", "))
    if len(deck) != 20:
        await ctx.respond("This deck doesn't have 20 cards!\nThe format is ``/add_deck <name> [\"card1\", \"<card2>\", \"<card3>\", until \"<card20>\"]``")
    else:
        with open("decks.json", "r") as f:
            deckdict = json.load(f)
            deckdict[name] = deck
        with open("decks.json", "w") as f:
            json.dump(deckdict, f)
        await ctx.respond(f"Deck {name} is saved.")





























bot.run("NzIxNDAzNzgzODY2NzQ0OTM1.GUsJE2.-6T6MHzfWGirEEsle5YBkWVS6jeYWn_u5r7Di8")