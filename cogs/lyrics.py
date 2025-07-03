# cogs/lyrics.py

import os
import re
import logging
import requests
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from session_manager import is_user_in_active_session
import openai

LYRICS_THREAD_ID = 1390448992520765501
GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")

if not GENIUS_API_TOKEN:
    logging.error("❌ GENIUS_API_TOKEN ontbreekt in je omgevingsvariabelen!")

class LyricsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {GENIUS_API_TOKEN}"})

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Alleen in de juiste thread
        if not (isinstance(message.channel, discord.Thread) and message.channel.id == LYRICS_THREAD_ID):
            return

        # Geen antwoord als user in actieve sessie zit
        if is_user_in_active_session(message.author.id):
            return

        # Check op YouTube-link
        youtube_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+"
        if not re.search(youtube_regex, message.content):
            return

        await message.channel.send("🎵 YouTube-link gevonden! Ik zoek de songtekst…")

        song_info = self.search_genius(message.content)
        if not song_info:
            await message.channel.send("⚠️ Geen song gevonden op Genius.")
            return

        lyrics = self.scrape_lyrics(song_info["url"])
        if not lyrics:
            await message.channel.send("⚠️ Kon de songtekst niet ophalen.")
            return

        translated = await self.translate_lyrics(lyrics)

        for chunk in self.split_into_chunks(translated, 1900):
            await message.channel.send(f"🎶\n{chunk}")

    def search_genius(self, youtube_url):
        try:
            resp = requests.get(youtube_url)
            title = re.search(r'<title>(.*?)</title>', resp.text)
            query = title.group(1) if title else youtube_url
        except Exception:
            query = youtube_url

        params = {"q": query}
        resp = self.session.get("https://api.genius.com/search", params=params)
        if resp.status_code != 200:
            return None
        hits = resp.json().get("response", {}).get("hits", [])
        if not hits:
            return None
        best = hits[0]["result"]
        return {"title": best["full_title"], "url": best["url"]}

    def scrape_lyrics(self, page_url):
        try:
            resp = self.session.get(page_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            lyrics_div = soup.find("div", class_="lyrics")
            if lyrics_div:
                raw = lyrics_div.get_text(separator="\n")
            else:
                raw = "\n".join([el.get_text() for el in soup.select("div[class^='Lyrics__Container']")])
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            return lines
        except Exception as e:
            logging.error(f"Fout bij scrapen van lyrics: {e}")
            return None

    async def translate_lyrics(self, lines):
        prompt = "\n".join(lines)
        system = (
            "Je bent een vertaler. Vertaal de Italiaanse songtekst regel voor regel. "
            "Onder elke originele regel zet je de Nederlandse vertaling tussen haakjes en _cursief_. "
            "Gebruik contextuele vertaling, niet woord-voor-woord."
        )
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Fout bij vertalen songtekst: {e}")
            return "⚠️ Fout bij vertalen."

    def split_into_chunks(self, text, max_length):
        paragraphs = text.split("\n\n")
        chunks, buffer = [], ""
        for para in paragraphs:
            block = para + "\n\n"
            if len(buffer) + len(block) > max_length:
                chunks.append(buffer.strip())
                buffer = block
            else:
                buffer += block
        if buffer:
            chunks.append(buffer.strip())
        return chunks

async def setup(bot):
    await bot.add_cog(LyricsCog(bot))