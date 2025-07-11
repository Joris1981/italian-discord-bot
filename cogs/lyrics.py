import discord
from discord.ext import commands
import re
import os
import openai
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_links = set()  # voorkomt herhaling van dezelfde link

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if str(message.channel.id) != "1390448992520765501":
            return

        print(f"🎵 Bericht ontvangen: {message.content}")

        yt_match = re.search(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)", message.content)
        if not yt_match:
            return

        # Link proper extraheren en controleren op duplicaat
        yt_url = yt_match.group(0).split("&")[0]
        if yt_url in self.recent_links:
            print("⚠️ Dubbele link gedetecteerd, wordt overgeslagen.")
            return
        self.recent_links.add(yt_url)

        title = await self.extract_youtube_title(message)
        if not title:
            await message.channel.send("❌ Kon de titel van het YouTube-nummer niet ophalen.")
            return

        await message.channel.send(f"\U0001F50D Lied herkend: **{title}**\nEen momentje, ik reconstrueer de tekst en vertaling…")

        lyrics = await self.generate_lyrics_with_translation(title)
        if not lyrics:
            await message.channel.send("❌ Sorry, ik kon geen songtekst reconstrueren.")
            return

        chunks = self.split_text(lyrics, max_length=1900)
        for chunk in chunks:
            await message.channel.send(chunk)

    async def extract_youtube_title(self, message):
        # Wacht indien embed nog niet klaar is
        for _ in range(2):
            if message.embeds and message.embeds[0].title:
                print("✅ Titel gevonden via Discord embed")
                return message.embeds[0].title.strip()
            await asyncio.sleep(1)

        # Fallback: YouTube scraping
        yt_url_match = re.search(r"(https?://[^\s]+)", message.content)
        if yt_url_match:
            raw_url = yt_url_match.group(1)
            clean_url = raw_url.split("&")[0]
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(clean_url, headers=headers) as resp:
                        text = await resp.text()
                        title_match = re.search(r"<title>(.*?)</title>", text)
                        if title_match:
                            print("✅ Titel gevonden via scraping")
                            return title_match.group(1).replace(" - YouTube", "").strip()
            except Exception as e:
                print(f"❌ Fout bij YouTube scraping: {e}")
        return None

    async def generate_lyrics_with_translation(self, title):
        try:
            prompt = (
                f"""Sto cercando il testo completo della canzone italiana intitolata "{title}". 
Genera fedelmente l'intero testo a partire dall'inizio, senza saltare strofe. 
Dopo ogni riga, fornisci la traduzione in olandese tra parentesi e in corsivo. 
Scrivi almeno 20 righe. Formato:

Riga in italiano  
(*Vertaling in het Nederlands*)"""
            )

            response = await openai.AsyncOpenAI().chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sei un esperto traduttore e paroliere. Ricostruisci testi fedeli e poetici, "
                            "senza saltare l'inizio, con traduzione dopo ogni riga tra parentesi in corsivo."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3072
            )
            print("✅ Lyrics succesvol gegenereerd via OpenAI")
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