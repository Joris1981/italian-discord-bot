# cogs/lyrics.py

import discord
from discord.ext import commands
import re
import os
import openai
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY ontbreekt in .env!")

client = openai.OpenAI(api_key=openai_api_key)

LYRICS_THREAD_ID = 1390448992520765501

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if str(message.channel.id) != str(LYRICS_THREAD_ID):
            return

        yt_match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)", message.content)
        sp_match = re.search(r"(https?://open\.spotify\.com/track/[a-zA-Z0-9]+)", message.content)

        if yt_match:
            title = await self.extract_youtube_title(message)
        elif sp_match:
            title = await self.extract_spotify_title(message)
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

        for chunk in self.split_text(lyrics, max_length=1900):
            await message.channel.send(chunk)

    async def extract_youtube_title(self, message):
        if message.embeds:
            return message.embeds[0].title
        return None

    async def extract_spotify_title(self, message):
        try:
            embed = message.embeds[0]
            return f"{embed.title} di {embed.author.name}" if embed and embed.title and embed.author else None
        except Exception:
            return None

    async def generate_lyrics_with_translation(self, title):
        prompt = (
            f'Il brano si intitola "{title}". Genera una canzone italiana coerente con questo titolo. '
            "Dopo ogni riga italiana, inserisci la traduzione in olandese tra parentesi e in corsivo. "
            "Mantieni il tono poetico. Scrivi almeno 20 versi. Formaat:\n\n"
            "Italiano\n(*Nederlandse vertaling*)"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un poeta e traduttore italiano. Scrivi testi poetici con traduzione olandese dopo ogni riga."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ OpenAI fout: {e}")
            return None

    def split_text(self, text, max_length=1900):
        lines = text.split("\n")
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 <= max_length:
                current += line + "\n"
            else:
                chunks.append(current.strip())
                current = line + "\n"
        if current:
            chunks.append(current.strip())
        return chunks

async def setup(bot):
    await bot.add_cog(Lyrics(bot))