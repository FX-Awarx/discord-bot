from flask import Flask
from threading import Thread
import discord
import requests
import os

# Flask pour keep-alive
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

TOKEN = os.environ["DISCORD_TOKEN"]

# Intents étendus
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# Dictionnaire pour stocker les cryptos suivies par chaque user
user_crypto_tracking = {}

@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

    # Épingler les commandes dans #commandes
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name="commandes")
        if channel:
            messages = await channel.history(limit=50).flatten()
            already_pinned = any(m.pinned for m in messages)
            if not already_pinned:
                msg = await channel.send("📌 Tape `!help` pour voir toutes les commandes. Commence avec `!track btc` pour suivre le Bitcoin.")
                await msg.pin()

@client.event
async def on_member_join(member):
    try:
        # Message dans #bienvenue
        welcome_channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
        if welcome_channel:
            await welcome_channel.send(f"👋 Bienvenue {member.mention} sur **{member.guild.name}** !")

        # Message privé d’intro
        await member.send(
            f"👋 Salut {member.name} ! Bienvenue sur **{member.guild.name}**.\n\n"
            "Je suis **CryptoBot**, ici pour t'aider à suivre les cryptos, devises ou monnaies d’échange.\n\n"
            "**Voici comment commencer :**\n"
            "`!track btc` → Pour suivre le Bitcoin\n"
            "`!track eth` → Pour suivre l’Ethereum\n"
            "Tu peux en suivre plusieurs. Je t’enverrai automatiquement leur valeur à chaque fois que tu rejoins le serveur.\n\n"
            "Tape `!help` dans un salon pour voir toutes les commandes disponibles 📈"
        )
    except Exception as e:
        print(f"Erreur message de bienvenue : {e}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()
    user_id = message.author.id

    if msg.startswith("!ping"):
        await message.channel.send("🏓 Pong ! Je suis en ligne.")

    elif msg.startswith("!help"):
        await message.channel.send("""📖 **Commandes disponibles :**
`!track <crypto>` → Commence à suivre une crypto (btc, eth, usdt...)
`!untrack <crypto>` → Arrête de suivre une crypto
`!mycryptos` → Liste des cryptos que tu suis
`!ping` → Vérifie si je suis actif
`!info` → À propos du bot
`!say <texte>` → Je répète ton message
`!avatar` → Ton avatar
`!server` → Infos du serveur
`!userinfo @user` → Infos d’un membre
`!suggest <texte>` → Soumettre une idée
`!announce <msg>` → Envoie une annonce (admin)
`!dm @membre <msg>` → Message privé (admin)
""")

    elif msg.startswith("!track"):
        try:
            crypto = msg.split(" ")[1].lower()
            user_crypto_tracking.setdefault(user_id, set()).add(crypto)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            data = requests.get(url).json()
            price = data[crypto]["usd"]
            await message.channel.send(f"✅ Tu suis maintenant **{crypto.upper()}** → {price}$")
        except:
            await message.channel.send("❌ Crypto non reconnue ou erreur API.")

    elif msg.startswith("!untrack"):
        try:
            crypto = msg.split(" ")[1].lower()
            if user_id in user_crypto_tracking and crypto in user_crypto_tracking[user_id]:
                user_crypto_tracking[user_id].remove(crypto)
                await message.channel.send(f"❌ Tu ne suis plus **{crypto.upper()}**.")
            else:
                await message.channel.send("⚠️ Tu ne suis pas cette crypto.")
        except:
            await message.channel.send("❌ Commande incorrecte. Utilise `!untrack btc` par exemple.")

    elif msg.startswith("!mycryptos"):
        cryptos = user_crypto_tracking.get(user_id, set())
        if cryptos:
            await message.channel.send(f"📊 Tu suis actuellement : {', '.join(c.upper() for c in cryptos)}")
        else:
            await message.channel.send("📭 Tu ne suis aucune crypto pour le moment.")

    elif msg.startswith("!info"):
        await message.channel.send("🤖 Je suis CryptoBot, conçu pour aider les traders à suivre les cours des monnaies d’échange.")

    elif msg.startswith("!say "):
        await message.channel.send(msg[5:])

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

# Lancer le bot
client.run(TOKEN)
