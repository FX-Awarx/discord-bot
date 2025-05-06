from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne (keep alive actif)"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

import discord
import requests
import os
import os
TOKEN = os.environ["DISCORD_TOKEN"]


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

    if msg.startswith("!ping"):
        await message.channel.send("🏓 Pong ! Je suis en ligne.")

    elif msg.startswith("!help"):
        await message.channel.send("""📖 **Commandes disponibles :**
`!track <crypto>` → Prix crypto (btc, eth, etc.)
`!ping` → Vérifie si je suis en ligne
`!info` → À propos du bot
`!say <texte>` → Je répète ce que tu dis
`!avatar` → Ton avatar
`!server` → Infos du serveur
`!userinfo @user` → Infos sur un membre
`!suggest <texte>` → Propose une idée
`!announce <msg>` → Envoie une annonce (admin)
`!dm @membre <msg>` → Envoie un message privé (admin)
""")

    elif msg.startswith("!track"):
        try:
            crypto = msg.split(" ")[1]
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            data = requests.get(url).json()
            price = data[crypto]["usd"]
            await message.channel.send(f"💰 Prix de {crypto.upper()} : {price}$")
        except:
            await message.channel.send("❌ Crypto non reconnue ou erreur API.")

    elif msg.startswith("!info"):
        await message.channel.send("🤖 Je suis un bot développé par un lycéen ambitieux avec l'aide de ChatGPT !")

    elif msg.startswith("!say "):
        to_say = msg[5:]
        await message.channel.send(to_say)

    elif msg.startswith("!avatar"):
        await message.channel.send(message.author.avatar.url)

    elif msg.startswith("!server"):
        server = message.guild
        await message.channel.send(f"📌 Nom : {server.name} | Membres : {server.member_count}")

    elif msg.startswith("!userinfo"):
        if message.mentions:
            user = message.mentions[0]
            await message.channel.send(f"👤 {user.name}#{user.discriminator} | ID: {user.id}")
        else:
            await message.channel.send("🔍 Mentionne quelqu’un pour voir ses infos.")

    elif msg.startswith("!suggest "):
        suggestion = msg[9:]
        chan = discord.utils.get(message.guild.text_channels, name="suggestions")
        if chan:
            await chan.send(f"💡 Suggestion de {message.author.mention} : {suggestion}")
            await message.channel.send("✅ Suggestion envoyée !")
        else:
            await message.channel.send("⚠️ Le salon `#suggestions` n'existe pas.")

    elif msg.startswith("!announce "):
        if message.author.guild_permissions.administrator:
            annonce = msg[10:]
            chan = discord.utils.get(message.guild.text_channels, name="annonces")
            if chan:
                await chan.send(f"📢 Annonce : {annonce}")
            else:
                await message.channel.send("⚠️ Le salon `#annonces` n'existe pas.")
        else:
            await message.channel.send("⛔ Tu dois être admin pour faire ça.")

    elif msg.startswith("!dm "):
        if message.author.guild_permissions.administrator:
            try:
                user = message.mentions[0]
                contenu = " ".join(msg.split(" ")[2:])
                await user.send(f"✉️ Message de {message.author.name} : {contenu}")
                await message.channel.send("✅ Message envoyé.")
            except:
                await message.channel.send("⚠️ Erreur d'envoi (mention manquante ?).")
        else:
            await message.channel.send("⛔ Tu dois être admin pour utiliser cette commande.")
    