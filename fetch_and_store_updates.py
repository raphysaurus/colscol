import os
import aiohttp
import asyncio
import logging
import xml.etree.ElementTree as ET 

from dotenv import load_dotenv
from datetime import datetime
from database import db, ArxivUpdate

load_dotenv()

base_url = os.getenv("FEED_BASE_URL")
namespaces = {"dc": "http://purl.org/dc/elements/1.1/"}
topics = ["math.CT", "math.QA"]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("RSS-Feed")

for t in [ArxivUpdate]:
    if not db.table_exists(t):
        db.create_tables([t])

async def fetch_feed(session: aiohttp.ClientSession, topic: str):
    feed_url = base_url + topic
    async with session.get(feed_url) as resp:
        if resp.status == 200:
            content = await resp.text()
            xml_tree = ET.fromstring(content)
            items = xml_tree.findall(".//item")
            for item in items:
                title = item.find(".//title").text
                authors = item.find(".//dc:creator", namespaces).text
                abstract = item.find(".//description").text
                abstract = abstract.split("\n", 1)[1]
                link  = item.find(".//link").text
                try:
                    with db.atomic():
                        ArxivUpdate.create(
                            date=datetime.today().strftime('%Y-%m-%d'),
                            topic = topic,
                            title=title,
                            authors=authors,
                            abstract=abstract,
                            link=link)
                    logger.info("All records have been saved.")
                except Exception as e:
                    print(e)
        else:
            logger.error(f"Unable to fetch update: {resp.status} {resp.reason}")

async def main():
    async with aiohttp.ClientSession() as sess:
        async with asyncio.TaskGroup() as tg:
            for topic in topics:
                tg.create_task(fetch_feed(sess, topic))
    
asyncio.run(main())