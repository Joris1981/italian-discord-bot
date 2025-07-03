import discord
from discord.ext import commands
import re
import os
import openai
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Detecteer YouTube of Spotify links
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Alleen in specifieke thread
        if str(message.channel.id) != "1390448992520765501":
            return

        yt_match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)", message.content)
        sp_match = re.search(r"(https?://open\.spotify\.com/track/[a-zA-Z0-9]+)", message.content)

        if yt_match:
            title = await self.extract_youtube_title(message)
        elif sp_match:
            title = await self.extract_spotify_title(message.content)
        else:
            return

        if not title:
            await message.channel.send("❌ Kon de titel van het nummer niet ophalen.")
            return

        await message.channel.send(f"🔎 Lied herkend: **{title}**\nEen momentje, ik reconstrueer de tekst en vertaling…")

        lyrics = await self.generate_lyrics_with_translation(title)
        if not lyrics:
            await message.channel.send("❌ Sorry, ik kon geen songtekst reconstrueren.")
            return

        chunks = self.split_text(lyrics, max_length=1900)
        for chunk in chunks:
            await message.channel.send(chunk)

    # Simuleer extractie van titel bij YouTube (via Discord metadata)
    async def extract_youtube_title(self, message):
        if message.embeds:
            return message.embeds[0].title
        return None

    # Spotify title ophalen uit metadata (indien beschikbaar)
    async def extract_spotify_title(self, url):
        try:
            headers = {"Accept": "application/json"}
            async with self.bot.session.get(url, headers=headers) as resp:
                html = await resp.text()
                title_match = re.search(r'"name":"(.*?)".*?"artists":\[{"name":"(.*?)"', html)
                if title_match:
                    song = title_match.group(1)
                    artist = title_match.group(2)
                    return f"{song} di {artist}"
        except Exception:
            return None

    # Gebruik OpenAI om lyrics te genereren en vertalen
    async def generate_lyrics_with_translation(self, title):
        try:
            prompt = f"""Il brano si intitola "{title}". Genera una canzone italiana coerente con questo titolo. Dopo ogni riga italiana, inserisci una traduzione in olandese tra parentesi e in corsivo. Mantieni il tono poetico. Esempio:

Giorni d'estate così caldi  
(*Zulke warme zomerdagen*)

Scrivi almeno 20 versi, formato:  
Italiano  
(*Nederlandse vertaling*)  
"""

            response = await openai.AsyncOpenAI().chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un poeta e traduttore italiano. Scrivi canzoni coerenti, poetiche e con una traduzione dopo ogni verso."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ OpenAI fout: {e}")
            return None

    # Splits lange tekst in blokken
    def split_text(self, text, max_length=1900):
        lines = text.split("\n")
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 <= max_length:
                current += line + "\n"
            else:
                chunks.append(current)
                current = line + "\n"
        if current:
            chunks.append(current)
        return chunks

async def setup(bot):
    await bot.add_cog(Lyrics(bot))