import asyncio
import datetime
import requests
import time
import traceback

from .db import DB
from .utils import LoggingHandler

from requests_html import HTMLSession, AsyncHTMLSession


class Downloader(LoggingHandler):
    item_url = None
    criteria = []

    session = HTMLSession()
    asession = AsyncHTMLSession()

    # Configure the session preferences
    adapter = requests.adapters.HTTPAdapter(
        max_retries=10, pool_connections=100, pool_maxsize=100
    )
    asession.mount('http://', adapter)
    asession.mount('https://', adapter)

    # Variables to be defined by sub-sub-classes
    db_name = None
    orderField = None
    stateField = None
    url_name = None

    def __init__(self):
        # Initialise LoggingHandler
        super(Downloader, self).__init__()
        self.refs = []  # initialise here otherwise cumulative effect

        # Initialise urls
        self._init_urls()

        # Initialise DB connection
        self.db = DB("postgresql://admin:@localhost:5435/", self.db_name, "fatawa")

        # Check that criteria isn't empty
        if not self.criteria:
            raise Exception("Criteria array is empty")

    def _init_urls(self):
        """Initialise urls"""
        raise Exception("To be implemented")

    async def get_refs_each(self, item, lastUpdate):
        """Downloads references and add to result set"""
        raise Exception("To be implemented")

    async def get_refs_all(self, lastUpdate):
        """Iter through criteria and run the get_refs_each on each"""
        await asyncio.gather(
            *tuple(
                asyncio.ensure_future(self.get_refs_each(item, lastUpdate))
                for item in self.criteria
            ),
            return_exceptions=True
        )

    def get_refs(self, debug=False):
        """Gets references
        """
        # Get last updated time from DB
        row = self.db.db['last_update'].find_one(id=1)

        # Set default date if last update doesn't exist
        lastUpdate = row['lastUpdate'] if row else self.default_datetime

        # Collect references
        start = time.time()
        asyncio.get_event_loop().run_until_complete(
            self.get_refs_all(lastUpdate)
        )

        # Sort results (ascending order, 1-n)
        self.refs = sorted(self.refs)

        self.log.info(f'Got {len(self.refs)} references')
        self.log.info(
            f'Getting references took {time.time()-start} secs'
        )

    def process_item_data(self, db, ref, response):
        """Processes the response data for each item"""
        raise Exception("To be implemented")

    async def get_item_data(self, ref, db):
        """Downloads items and add to the db"""
        response = await self.asession.get(self.item_url.format(ref))

        if response.status_code == 404:
            return self.log.debug(f"Item {ref} doesn't exist")

        try:
            # Raise for other response failures
            response.raise_for_status()

            # Add item to the db
            self.process_item_data(db, ref, response)

            self.log.debug(f'Got item {ref}')
        except Exception:
            e = traceback.format_exc()
            self.log.error(f'{e} (item {ref}, status {response.status_code})')

    async def get_items_data(self, db):
        """Iter through references and run the get_item_data function on each"""
        await asyncio.gather(
            *tuple(
                asyncio.ensure_future(self.get_item_data(ref, db))
                for ref in self.refs
            ),
            return_exceptions=True
        )

    def get_items(self, debug=False):
        """Gets items data"""
        # Time of last update to the DB
        lastUpdate = datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")

        # Get items data
        start = time.time()
        asyncio.get_event_loop().run_until_complete(
            self.get_items_data(self.db)
        )

        self.log.info(f'Got {len(self.refs)} references')
        self.log.info(f'Getting items data took {time.time()-start} secs')

        # Insert into DB
        start = time.time()
        self.db.commit()

        # Update the lastUpdate time
        self.db.db['last_update'].upsert(
            dict(id=1, lastUpdate=lastUpdate), ['id']
        )

        self.log.info(f'Data upsert into the DB took {time.time()-start} secs')

    def download(self):
        # Get items and insert them into the DB
        self.get_refs()
        self.get_items()