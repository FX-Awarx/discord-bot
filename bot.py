from flask import Flask
from threading import Thread
import discord
import requests
import os
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import datetime

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

@client.event
async def on_member_join(member):
    try:
        welcome_channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
        if welcome_channel:
            await welcome_channel.send(f"👋 Bienvenue {member.mention} sur **{member.guild.name}** ! Pense à lire le salon #règles pour débloquer l'accès au reste.")

        await member.send(
            f"👋 Salut {member.name}, bienvenue sur **{member.guild.name}** !\n\nJe suis CryptoBot. Tu peux suivre des cryptos avec la commande `!track <nom>` ou demander un graphique avec `!graph <nom>`\nTape `!help` dans un salon pour voir toutes mes commandes."
        )
    except:
        print(f"❌ Erreur lors du message de bienvenue à {member.name}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()

    if msg.startswith("!ping"):
        await message.channel.send("🏓 Pong ! Je suis en ligne.")

    elif msg.startswith("!help"):
        await message.channel.send("""📖 **Commandes disponibles :**
`!track <crypto>` → Affiche le prix actuel
`!graph <crypto>` → Reçoit une courbe des 7 derniers jours en DM
`!listcryptos` → Voir les cryptos populaires
`!info` → À propos du bot
""")

    elif msg.startswith("!track"):
        try:
            crypto = msg.split(" ")[1].lower()
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            data = requests.get(url).json()
            if crypto in data:
                price = data[crypto]["usd"]
                await message.channel.send(f"📈 **{crypto.upper()}** → {price}$")
            else:
                await message.channel.send("❌ Crypto non reconnue. Tape `!listcryptos` pour des exemples.")
        except:
            await message.channel.send("⚠️ Erreur lors de la récupération. Utilise par exemple `!track bitcoin`.")

    elif msg.startswith("!graph"):
        try:
            crypto = msg.split(" ")[1].lower()
            url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=7"
            data = requests.get(url).json()
            prices = data.get("prices", [])

            if not prices:
                await message.channel.send("❌ Aucune donnée disponible pour cette crypto.")
                return

            dates = [datetime.datetime.fromtimestamp(p[0] / 1000) for p in prices]
            values = [p[1] for p in prices]

            plt.figure(figsize=(10, 4))
            plt.plot(dates, values, label=crypto.upper())
            plt.title(f"Évolution de {crypto.upper()} sur 7 jours")
            plt.xlabel("Date")
            plt.ylabel("Prix (USD)")
            plt.grid(True)
            plt.legend()

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            await message.author.send(file=discord.File(buf, filename=f"{crypto}_graph.png"))
            await message.channel.send("📈 Courbe envoyée en message privé !")

        except Exception as e:
            print(f"Erreur graphique : {e}")
            await message.channel.send("❌ Impossible de générer la courbe.")

    elif msg.startswith("!listcryptos"):
        await message.channel.send("""📊 Cryptos populaires :
- bitcoin
- ethereum
- solana
- bnb
- ripple
- dogecoin
- cardano
- avalanche
- tron
- polkadot
""")

    elif msg.startswith("!info"):
        await message.channel.send("🤖 Je suis CryptoBot, ton assistant pour suivre les cryptos et générer des graphiques en temps réel !")

client.run(TOKEN)
