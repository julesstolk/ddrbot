from code import interact
from ftplib import parse150
from gc import disable
import json
import os
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
    "banish": [],
    "notes": {}
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
    print(boardlist1)
    print(game["notes" + p2])
    for i in range(len(boardlist1)):
        if boardlist1[i] in game["notes" + p1].keys():
            boardlist1[i] = boardlist1[i] + " - " + game["notes" + p1][boardlist1[i]]
    for i in range(len(boardlist2)):
        if boardlist2[i] in game["notes" + p2].keys():
            boardlist2[i] = boardlist2[i] + " - " + game["notes" + p2][boardlist2[i]]
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
    @discord.ui.button(label="See hand", style=discord.ButtonStyle.primary)
    async def seehand_callback(self, button, interaction):
        game = load(interaction.channel)
        await interaction.response.send_message(content=game["hand" + str(interaction.user)[0:-5].lower()], ephemeral=True)

    @discord.ui.button(label="See deck", style=discord.ButtonStyle.primary)
    async def seedeck_callback(self, button, interaction):
        game = load(interaction.channel)
        await interaction.response.send_message(content=game["deck" + str(interaction.user)[0:-5].lower()], ephemeral=True)

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
        
    @discord.ui.button(label="Move", style=discord.ButtonStyle.primary)
    async def move_callback(self, button, interaction):
        game = load(interaction.channel)
        p1, p2 = str(interaction.channel).split("-")
        cardsOnBoard = game["board" + p1]
        for i in range(len(cardsOnBoard)):
            cardsOnBoard[i] = discord.SelectOption(label=cardsOnBoard[i] + " - " + p1 + ", " + str(i + 1))
        for item in game["board" + p2]:
            cardsOnBoard.append(discord.SelectOption(label=item + " - " + p2 + ", " + str(game["board" + p2].indexof(item) + 1)))

        class chooseRemoveCard(discord.ui.View):

            @discord.ui.select(placeholder="Choose a card to move.", min_values=1, max_values=1, options=cardsOnBoard)
            async def move_callback(self, select, interaction):
                game = load(interaction.channel)
                player = str(interaction.user)[0:-5].lower()
                chosenCard, subject = select.values[0].split(" - ")
                subject = subject[0:-3]
                if player == subject:
                    disableFriendlyButton = False
                else:
                    disableFriendlyButton = True

                class chooseMoveSubject(discord.ui.View):
                    @discord.ui.button(label="Grave", style=discord.ButtonStyle.primary)
                    async def grave_callback(self, button, interaction):
                        game["board" + subject].remove(chosenCard)
                        game["grave" + subject].append(chosenCard)
                        save(interaction.channel, game)
                        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())
                        
                    @discord.ui.button(label="Banish", style=discord.ButtonStyle.primary)
                    async def banish_callback(self, button, interaction):
                        game["board" + subject].remove(chosenCard)
                        game["banish" + subject].remove(chosenCard)
                        save(interaction.channel, game)
                        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

                    @discord.ui.button(label="Exile", style=discord.ButtonStyle.primary)
                    async def exile_callback(self, button, interaction):
                            game["board" + subject].remove(chosenCard)
                            game["board" + subject].append("EXILED")
                            save(interaction.channel, game)
                            await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

                    @discord.ui.button(label="Hand", style=discord.ButtonStyle.primary, disabled=disableFriendlyButton)
                    async def hand_callback(self, button, interaction):
                        game["board" + subject].remove(chosenCard)
                        game["hand" + subject].append(chosenCard)
                        save(interaction.channel, game)
                        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

                    @discord.ui.button(label="Deck", style=discord.ButtonStyle.primary, disabled=disableFriendlyButton)
                    async def deck_callback(self, button, interaction):
                        game["board" + subject].remove(chosenCard)
                        game["deck" + subject].append(chosenCard)
                        save(interaction.channel, game)
                        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

                    @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
                    async def escape_callback(self, button, interaction):
                        await interaction.response.edit_message(view=buttonBoard())
                
                @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
                async def escape_callback(self, button, interaction):
                    await interaction.response.edit_message(view=buttonBoard())

                await interaction.response.edit_message(view=chooseMoveSubject())
        await interaction.response.edit_message(view=chooseRemoveCard())

    @discord.ui.button(label="Draw", style=discord.ButtonStyle.primary)
    async def draw_callback(self, button, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        drawncard = random.choice(game["deck" + player])
        game["deck" + player].remove(drawncard)
        game["hand" + player].append(drawncard)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))

    @discord.ui.button(label="Magic", style=discord.ButtonStyle.primary)
    async def magic_callback(self, button, interaction):
        await interaction.response.edit_message(view=editMagic())

    @discord.ui.button(label="Damage", style=discord.ButtonStyle.primary)
    async def damage_callback(self, button, interaction):
        await interaction.response.edit_message(view=damageView())

    @discord.ui.button(label="Search", style=discord.ButtonStyle.primary)
    async def search_callback(self, button, interaction):
        modal = searchModal(title="Search for a card.")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Edit deck", style=discord.ButtonStyle.primary)
    async def deck_callback(self, button, interaction):
        await interaction.response.edit_message(view=editDeck())

    @discord.ui.button(label="Note", style=discord.ButtonStyle.primary)
    async def note_callback(self, button, interaction):
        modal = addNote(title="Add a note to a card.")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="End Turn", style=discord.ButtonStyle.danger, row=2)
    async def endturn_callback(self, button, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        game["maxmagic" + player] += 1
        game["magic" + player] = game["maxmagic" + player]
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))

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

class editMagic(discord.ui.View):
    @discord.ui.button(label="Change magic", style=discord.ButtonStyle.primary)
    async def magic_callback(self, button, interaction):
        modal = magicModal(title="Change magic")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Change max magic", style=discord.ButtonStyle.primary)
    async def maxmagic_callback(self, button, interaction):
        modal = magicMaxModal(title="Change max magic")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
    async def escape_callback(self, button, interaction):
        await interaction.response.edit_message(view=buttonBoard())

class magicModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Edit your magic."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        game["magic" + player] = int(self.children[0].value)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

class magicMaxModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Edit your magic."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        game["maxmagic" + player] = int(self.children[0].value)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

class damageView(discord.ui.View):
    @discord.ui.button(label="Yourself", style=discord.ButtonStyle.primary)
    async def yourself_callback(self, button, interaction):
        modal = youDamageModal(title="Deal damage to yourself.")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Enemy", style=discord.ButtonStyle.primary)
    async def enemy_callback(self, button, interaction):
        modal = enemyDamageModal(title="Deal damage to your enemy.")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Escape", style=discord.ButtonStyle.danger)
    async def escape_callback(self, button, interaction):
        await interaction.response.edit_message(view=buttonBoard())

class youDamageModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Type the damage you want to deal."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        game["hp" + player] -= int(self.children[0].value)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

class enemyDamageModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Type the damage you want to deal."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        p1, p2 = str(interaction.channel).split("-")
        if player == p1:
            enemy = p2
        else: 
            enemy = p1
        game["hp" + enemy] -= int(self.children[0].value)
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel), view=buttonBoard())

class searchModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Type the card you want to search."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        if self.children[0].value in game["deck" + player]:
            game["deck" + player].remove(self.children[0].value)
            game["hand" + player].append(self.children[0].value)
            save(interaction.channel, game)
            await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))
        else:
            await interaction.response.send_message(content="That card is not in your deck.")

class addNote(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="The format is \"<cardname>-<note>\"."))

    async def callback(self, interaction):
        game = load(interaction.channel)
        player = str(interaction.user)[0:-5].lower()
        card, note = str(self.children[0].value).split("-")
        game["notes" + player][card] = note
        save(interaction.channel, game)
        await interaction.response.edit_message(content=makeBoardASCII(interaction.channel))

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
        await ctx.respond("This deck doesn't have 20 cards!\nThe format is ``/=add_deck <name> [\"card1\", \"card2\", \"card3\", until \"card20\"]``")
    else:
        with open("decks.json", "r") as f:
            deckdict = json.load(f)
            deckdict[name] = deck
        with open("decks.json", "w") as f:
            json.dump(deckdict, f)
        await ctx.respond(f"Deck {name} is saved.")





























bot.run("NzIxNDAzNzgzODY2NzQ0OTM1.GUsJE2.-6T6MHzfWGirEEsle5YBkWVS6jeYWn_u5r7Di8")