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
    logging.error("❌ GENIUS_API_TOKEN ontbreekt in .env!")

class LyricsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {GENIUS_API_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        self.openai_client = openai.OpenAI()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Alleen reageren in juiste thread
        if not (isinstance(message.channel, discord.Thread) and message.channel.id == LYRICS_THREAD_ID):
            return

        # Negeer als gebruiker in actieve sessie zit
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

        lyrics_lines = self.scrape_lyrics(song_info["url"])
        if not lyrics_lines:
            await message.channel.send("⚠️ Kon de songtekst niet ophalen.")
            return

        translated = await self.translate_lyrics(lyrics_lines)
        for chunk in self.split_into_chunks(translated, 1900):
            await message.channel.send(f"🎶\n{chunk}")

    def search_genius(self, youtube_url):
        try:
            resp = requests.get(youtube_url, headers={"User-Agent": "Mozilla/5.0"})
            title_match = re.search(r'<title>(.*?)</title>', resp.text)
            query = title_match.group(1) if title_match else youtube_url
        except Exception as e:
            logging.warning(f"Kon titel niet ophalen: {e}")
            query = youtube_url

        logging.info(f"🔎 Genius search: {query}")
        params = {"q": query}
        resp = self.session.get("https://api.genius.com/search", params=params)
        if resp.status_code != 200:
            logging.warning(f"❌ Genius API fout: {resp.status_code}")
            return None
        hits = resp.json().get("response", {}).get("hits", [])
        if not hits:
            return None
        best = hits[0]["result"]
        return {"title": best["full_title"], "url": f"https://genius.com{best['path']}"}

    def scrape_lyrics(self, page_url):
        try:
            resp = self.session.get(page_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            containers = soup.select("div[class^='Lyrics__Container']")
            if not containers:
                logging.warning("⚠️ Geen lyrics containers gevonden.")
                return None
            lines = []
            for div in containers:
                text = div.get_text(separator="\n").strip()
                for line in text.splitlines():
                    if line.strip():
                        lines.append(line.strip())
            return lines
        except Exception as e:
            logging.error(f"Fout bij scrapen van lyrics: {e}")
            return None

    async def translate_lyrics(self, lines):
        prompt = "\n".join(lines)
        system = (
            "Je bent een professionele vertaler. Vertaal elke regel van deze Italiaanse songtekst. "
            "Na elke regel zet je de Nederlandse vertaling tussen haakjes en cursief. Gebruik geen letterlijke vertaling, maar houd rekening met de betekenis in context."
        )
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Fout bij vertalen songtekst: {e}")
            return "⚠️ Fout bij vertalen van de tekst."

    def split_into_chunks(self, text, max_length):
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
            else:
                current_chunk += para + "\n\n"
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

async def setup(bot):
    await bot.add_cog(LyricsCog(bot))