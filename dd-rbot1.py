import random
import discord
from discord.ext import commands
import os
import json
# from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
from interactions import interactions, Button
from PIL import Image, ImageDraw, ImageFont


client = commands.Bot(command_prefix="=") 

starters = []
boardcomps = [
                [
                    Button(label = "See", style = 1, id = "see"), 
                    Button(label = "Play", style = 1, id = "playcard"),
                    Button(label = "Draw", style = 1, id = "drawcard"),
                    Button(label = "Remove", style = 1, id = "removecard"),
                    Button(label = "End Turn", style = 1, id = "end")
                ]
            ]

boardmessage = ""

font = ImageFont.truetype("assets/quicksand.ttf", 45)

def load(channel):
    channel = str(channel)
    with open(f"DDMatches/{channel}.json") as f:
        return json.load(f)

def save(channel, gamesav):
    with open(f"DDMatches/{channel}.json", "w") as f:
        json.dump(gamesav, f)

def boardgen(channel):
    gamesav = load(channel)
    P1, P2 = str(channel).split("-")
    output = f'''```
+----------------------------------------------------------------------------------------------+\n
| HP {P1}:{gamesav['HPP1']} | Hand:{len(gamesav['handP1'])} | Deck:{len(gamesav['deckP1'])} | Magic:{gamesav['magicP1']} | Max Magic:{gamesav['maxmagicP1']} | Grave:{len(gamesav['graveP1'])} | Banished:{len(gamesav['banishP1'])} |\n
+----------------------------------------------------------------------------------------------+\n
| {gamesav['boardP1'][0]} | {gamesav['boardP1'][1]} | {gamesav['boardP1'][2]} | {gamesav['boardP1'][3]} | {gamesav['boardP1'][4]} |\n
+----------------------------------------------------------------------------------------------+\n
| {gamesav['boardP2'][0]} | {gamesav['boardP2'][1]} | {gamesav['boardP2'][2]} | {gamesav['boardP2'][3]} | {gamesav['boardP2'][4]} |\n
+----------------------------------------------------------------------------------------------+\n
| HP {P2}:{gamesav['HPP2']} | Hand:{len(gamesav['handP2'])} | Deck:{len(gamesav['deckP2'])} | Magic:{gamesav['magicP2']} | Max Magic:{gamesav['maxmagicP2']} | Grave:{len(gamesav['graveP2'])} | Banished:{len(gamesav['banishP2'])} |\n
+----------------------------------------------------------------------------------------------+
```'''
    return output

def to_int(str):
    return int(str)

def savestart():
   with open("start.json", "w") as f:
        json.dump(starters, f)

def mktemp(player, P1, P2):
    if player == P1:
        return "P1"
    if player == P2:
        return "P2"


@client.event
async def on_ready():
    DiscordComponents(client)   
    print("{0.user} is online".format(client))


@client.command(aliases=["s"])
async def show(ctx, *card):
    card = "".join(card)
    card = card.lower()
    for item in os.listdir("Cards/"):
        if card in item:
            card = item
            break
    await ctx.send(file=discord.File(f"Cards/{card}"))


@client.command()
async def start(ctx):
    global starters
    await ctx.send(starters)


@client.command()
async def match(ctx, player):
    global starters
    with open("start.json", "w+") as f:
        try:
            starters = json.load(f)
        except:
            pass
    open("start.json", "w").close()
    author = ctx.author
    person = author.name
    search1 = f"{player}-{person}"
    search2 = f"{person}-{player}"
    if search1 in starters:
        search = f"{player}-{person}"
        starters.remove(search)
        with open(f"DDMatches/{search.lower()}.json", "w+") as f:
            f.write("{}")
        games = discord.utils.get(ctx.guild.categories, name="bot-stuff")
        ch = await ctx.channel.category.create_text_channel(search, position = 5)
        await ctx.send(f"Created the channel {ch}")
        startgame(search.lower())
        savestart()
    elif search2 in starters:
        search = f"{person}-{player}"
        starters.remove(search)
        with open(f"DDMatches/{search.lower()}.json", "w+") as f:
            f.write("{}")
        games = discord.utils.get(ctx.guild.categories, name="bot-stuff")
        ch = await ctx.channel.category.create_text_channel(search, position = 5)
        await ctx.send(f"Created the channel {ch}")
        startgame(search.lower())
        savestart()
    else:
        search = f"{person}-{player}"
        starters.append(search)
        savestart()
        await ctx.send(f"You challenged \"{player}\" to a match.")


def startgame(channel):
    with open(f"DDMatches/{channel}.json", "w") as f:
        gamesav = {
            'HPP1' : 20,
            'HPP2' : 20,
            'boardP1'   : ["--+--", "--+--", "--+--", "--+--", "--+--"],
            'boardP2'   : ["--+--", "--+--", "--+--", "--+--", "--+--"],
            'handP1'    : [],
            'handP2'    : [],
            'deckP1'    : [],
            'deckP2'    : [],
            'magicP1'    : 1,
            'magicP2'    : 1,
            'maxmagicP1' : 1,
            'maxmagicP2' : 1,
            'graveP1'   : [],
            'graveP2'   : [],
            'banishP1'  : [],
            'banishP2'  : []
        }
    save(channel, gamesav)

def buttongen(int, x, gamesav):
    list1 = []
    for i in range(0, 5):
        list1.append(Button(label = gamesav[f'boardP{x}'][i], style = 1, id = f"P{x}{int.component.id}{i}"))
    return list1

def selectgen(int, gamesav, temp):
    hand = gamesav["hand" + temp]
    opt = []
    for x in range(0, len(hand)):
            opt.append(SelectOption(label=x+1, value=f"choosecard{x}"))
    opt.append(SelectOption(label="Cancel", value=f"choosecardcancel"))
    return opt

def selectdraw(int):
    amt = []
    for x in range(0, 10):
        amt.append(SelectOption(label=x+1, value=f"drawcard{x}"))
    amt.append(SelectOption(label="Cancel", value=f"drawcardcancel"))
    return amt

def playcomp(int, card):
    global boardmessage
    gamesav = load(int.channel)
    P1, P2 = str(int.channel).split("-")
    temp = mktemp(str(int.user)[0:-5].lower(), P1, P2)
    if "--+--" in gamesav["board" + temp]:
        if card in gamesav["hand" + temp]:
            index = gamesav["board" + temp].index("--+--")
            gamesav["board" + temp][index] = card
            gamesav["hand" + temp].remove(card)
            save(int.channel, gamesav)
            return None
        else:
            return f"You don't have {card} in your hand"
    else:
        return "You don't have enough space on your board"


def generateboard(channel):
    bg = Image.open("assets/bgcards.png")
    gamesav = load(channel)
    for x in range(len(gamesav['boardP1'])):
        card = Image.open("assets/" + gamesav['boardP1'][x].strip(" ").lower() + ".png")
        bg.paste(card, (355+712*x, 233))
    for x in range(len(gamesav['boardP2'])):
        card = Image.open("assets/" + gamesav['boardP2'][x].strip(" ").lower() + ".png")
        bg.paste(card, (355+712*x, 1324))
    bg.save("assets/sendboard.png", quality=100)

@client.event
async def on_button_click(int):             # Main buttons
    global boardmessage
    gamesav = load(int.channel)
    P1, P2 = str(int.channel).split("-")
    temp = mktemp(str(int.user)[0:-5].lower(), P1, P2)
    if int.component.id == "see":
        await boardmessage.edit(boardgen(int.channel),
        components = [
            [
                Button(label = "Hand", style = 1, id = "showhand"),
                Button(label = "Deck", style = 1, id = "showdeck") 
            ]
        ])
        await int.respond(type=6)
    elif int.component.id == "showdeck":
        deck = gamesav["deck" + temp]
        deck = ", ".join(deck)
        await int.respond(content = deck)
        await boardmessage.edit(boardgen(int.channel), components = boardcomps)
        await int.respond(type=6)
    elif int.component.id == "showhand":
        hand = gamesav["hand" + temp]
        out = ""
        for x in range(0, len(hand)):
            out += f"{x+1}: {hand[x]} | "
        out = out[:-3]
        if out != "":
            await int.respond(content = out)
        else:
            await int.respond(content = "Your hand is empty!")
        await boardmessage.edit(boardgen(int.channel), components = boardcomps)
        await int.respond(type=6)
    elif int.component.id == "playcard":
        await boardmessage.edit(boardgen(int.channel),
            components = [Select(placeholder = "Select your card number", 
            options = selectgen(int, gamesav, temp)
                )
            ]
        )
        await int.respond(type=6)
    elif int.component.id == "drawcard":
        out = ""
        try:
            ran = random.choice(gamesav["deck" + temp])
            gamesav["deck" + temp].remove(ran)
            gamesav["hand" + temp].append(ran)
            out = out + f"You've drawn ||{ran}||\n"
        except:
            await int.respond("**Your deck is empty**")
        save(int.channel, gamesav)
        await boardmessage.edit(boardgen(int.channel), components = boardcomps)
        await int.respond(type=6)
    elif int.component.id == "removecard":
        await boardmessage.edit(boardgen(int.channel),
            components = [
                [
                    Button(label = "Grave", style = 1, id = "grave"),
                    Button(label = "Banish", style = 1, id = "banish"),
                    Button(label = "Exile", style = 1, id = "exile")
                ]

            ]
        )
        await int.respond(type=6)
    elif int.component.id == "grave" or int.component.id == "banish" or int.component.id == "exile":
        await boardmessage.edit(boardgen(int.channel),
            components = [
                buttongen(int, 1, gamesav),
                buttongen(int, 2, gamesav)
            ]
        
        )
        await int.respond(type=6)
    elif any(x in int.component.id for x in ["grave", "banish", "exile"]):
        tempo = int.component.id
        tempo1 = to_int(tempo[-1:])     # 0/1/2/3/4
        tempo2 = tempo[:2]              # P1/P2
        tempo3 = tempo[2:-1]            # Grave/Banish/Exile
        if tempo3 == "exile":
            if gamesav["board" + tempo2][tempo1] != "--+--":
                gamesav["board" + tempo2][tempo1] = "EXILED"
                save(int.channel, gamesav)
                await boardmessage.edit(boardgen(int.channel), components = boardcomps)
                await int.respond(type=6)
            else:
                await int.respond("There is no card on that place!")
                await int.respond(type=6)
        else:
            gamesav[tempo3 + tempo2].append(gamesav["board" + tempo2][tempo1])
            gamesav["board" + tempo2][tempo1] = "--+--"
            save(int.channel, gamesav)
            await boardmessage.edit(boardgen(int.channel), components = boardcomps)
            await int.respond(type=6)


@client.event
async def on_select_option(int):
    global boardmessage
    gamesav = load(int.channel)
    P1, P2 = str(int.channel).split("-")
    temp = mktemp(str(int.user)[0:-5].lower(), P1, P2)
    if "choosecard" in int.values[0]:
        choice = int.values[0]
        choice = choice.replace("choosecard", "")
        if not choice == "cancel":
            choice = to_int(choice)
            choice = gamesav["hand" + temp][choice]
            msg = playcomp(int, choice)
            if msg != None:
                await int.respond(content = msg)
        await boardmessage.edit(boardgen(int.channel), components = boardcomps)
        await int.respond(type=6)


# @client.command()
# async def board(ctx):
#     global boardmessage
#     gamesav = load(ctx.channel)
#     if boardmessage == "":
#         boardmessage = await ctx.send(boardgen(ctx.channel), components = boardcomps)
#     else:
#         boardmessage = await boardmessage.edit(boardgen(ctx.channel), components = boardcomps)


@client.command()
async def board(ctx):
    gamesav = load(ctx.channel)
    generateboard(ctx.channel)
    await ctx.send(file=discord.File("assets/sendboard.png", components = boardcomps))


@client.command(aliases=["summon"])
async def play(ctx, *card):
    global boardmessage
    card = " ".join(card)
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    if "--+--" in gamesav["board" + temp]:
        if card in gamesav["hand" + temp]:
            index = gamesav["board" + temp].index("--+--")
            gamesav["board" + temp][index] = card
            gamesav["hand" + temp].remove(card)
        else:
            await ctx.send(f"You don't have {card} in your hand")
    else:
        await ctx.send("You don't have enough space on your board")
    save(ctx.channel, gamesav)
    await boardmessage.edit(boardgen(ctx.channel), components = boardcomps)


@client.command()
async def destroy(ctx, player, pos):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    pos = int(pos) - 1
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    try:
        gamesav["grave" + temp].append(gamesav["board" + temp][pos])
        gamesav["board" + temp][pos] = "--+--"
    except:
        await ctx.send("That card is not on board")
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def delete(ctx):
    name = ctx.channel
    cname = str(name)
    os.remove(f"DDMatches/{cname}.json")
    await name.delete()


@client.command(aliases=["d"])
async def display(ctx, item):
    item = item.lower()
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    try:
        item = ", ".join(gamesav[item + temp])
    except:
        item = gamesav[item + temp]
    if item != "":
        await ctx.send("||" + item + "||")
    else:
        await ctx.send(f"Your {item} is empty!")


@client.command(aliases=["ad"])
async def adddeck(ctx, *cards):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    cardsstr = "".join(cards)
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    if "/" in cardsstr:
        cards = " ".join(cards)
        gamesav["deck" + temp].extend(list(cards.split("/")))
        cards = list(cards.split("/"))
    else:
        cards = " ".join(cards)
        gamesav["deck" + temp].append(cards)
        cards = "||" + cards + "||"
    save(ctx.channel, gamesav)
    await ctx.send(f"Added {cards} to deck")


@client.command()
async def draw(ctx, amt=1):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    out = ""
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    try:
        for x in range(0, amt):
            ran = random.choice(gamesav["deck" + temp])
            gamesav["deck" + temp].remove(ran)
            gamesav["hand" + temp].append(ran)
            out = out + f"You've drawn ||{ran}||\n"
    except:
        await ctx.send("**Your deck is empty**")
    save(ctx.channel, gamesav)
    await board(ctx)


@client.command(aliases=["m"])
async def magic(ctx, amt):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    amt = int(amt)
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    gamesav["magic" + temp] = gamesav["magic" + temp] + amt
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def hp(ctx, player, amt):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    player = player.lower()
    amt = int(amt)
    temp = mktemp(player, P1, P2)
    gamesav["HP" + temp] = gamesav["HP" + temp] + amt
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def maxmagic(ctx, amt):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    amt = int(amt)
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    gamesav["maxmagic" + temp] = gamesav["maxmagic" + temp] + amt
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def turn(ctx):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    gamesav["maxmagic" + temp] = gamesav["maxmagic" + temp] + 1
    gamesav["magic" + temp] = gamesav["maxmagic" + temp]
    try:
        ran = random.choice(gamesav["deck" + temp])
        gamesav["deck" + temp].remove(ran)
        gamesav["hand" + temp].append(ran)
        out = f"You've drawn ||{ran}||\n"
    except:
        await ctx.send("**Your deck is empty**")
        out = ""
    save(ctx.channel, gamesav)
    await ctx.send(out + boardgen(ctx.channel))


@client.command()
async def search(ctx, *card):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    card = " ".join(card)
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    if card in gamesav["deck" + temp]:
        gamesav["deck" + temp].remove(card)
        gamesav["hand" + temp].append(card)
    else:
        await ctx.send(f"{card} is not in your deck")
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def reset(ctx):
    startgame(ctx.channel)
    await ctx.send("Game is set up!")


@client.command()
async def remove(ctx, *card):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    card = " ".join(card)
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    try:
        gamesav["deck" + temp].remove(card)
        gamesav["banish" + temp].append(card)
    except:
        await ctx.send("That card is not in your deck")
    save(ctx.channel, gamesav)
    await ctx.send(boardgen(ctx.channel))


@client.command()
async def banish(ctx, player, pos):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    try:
        gamesav["banish" + temp].append(gamesav["board" + temp][pos])
        gamesav["board" + temp][pos] = "--+--"
    except:
        await ctx.send("That card is not on board")
    save(ctx.channel)
    await ctx.send(boardgen(ctx.channel))


@client.command(aliases=["ud"])
async def usedeck(ctx, deck):
    gamesav = load(ctx.channel)
    P1, P2 = str(ctx.channel).split("-")
    temp = mktemp(ctx.author.name.lower(), P1, P2)
    deck = deck.replace("|", "")
    decks = json.load(open("decks.json", "r"))
    gamesav["deck" + temp] = decks[deck]
    save(ctx.channel, gamesav)
    await ctx.send("Loaded deck ||" + ", ".join(gamesav["deck" + temp]) + "||")


@client.command(aliases=["cd"])
async def createdeck(ctx, name, *cards):
    cards = " ".join(cards)
    deck = list(cards.split("/"))
    if len(deck) == 20:
        with open("decks.json") as f:
            decks = json.load(f)
            decks[name] = deck
            await ctx.send(f"Deck created!")
            with open("decks.json", "w") as f:
                json.dump(decks, f)
    else:
        await ctx.send(f"That deck is not 20 cards long, it contains {len(deck)} cards")


@client.command()
async def close(ctx):
    games = os.listdir("DDMatches/")
    gamelist = []
    for item in games:
        gamelist.append(item[0:-5])
    print(gamelist)
    if ctx.channel.name in gamelist:
        await ctx.channel.delete()
    else:
        await ctx.send("You can't delete this channel idiot")

def draftfunc(ctx, name, dec, P1, P2, channel):
    print(channel)
    gamesav = load(channel)
    temp = mktemp(name, P1, P2)
    cards = os.listdir("Cards")
    player = None
    if dec != "start":
        if name.lower() == player:
            gamesav["deck" + temp].append(eval("card" + dec))
            card1 = random.choice(cards)
            card2 = random.choice(cards)
            while card1 == card2:
                card2 = random.choice(cards)
            if player == P1:
                player = P2
            else:
                player = P1
            return f"{player}, choose: :one: {card1[0:-4]} - :two: {card2[0:-4]}"
    else:
        if gamesav["deckP1"] < 20:
            player = P1
            card1 = random.choice(cards)
            card2 = random.choice(cards)
            while card1 == card2:
                    card2 = random.choice(cards)
            return f"{player}, choose: {card1[0:-4]} - {card2[0:-4]}"
        else:
            return ""
    save(ctx.channel, gamesav)


@client.command()
async def draft(ctx, dec):
    P1, P2 = str(ctx.channel).split("-")
    mess = draftfunc(ctx, ctx.author.name.lower(), dec, P1, P2, ctx.channel)
    if mess == "":
        await ctx.send("Drafting has ended!")
    else:
        await ctx.send(mess)


interactions.Client(token="").start()
