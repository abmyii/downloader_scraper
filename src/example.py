import flatdict
import json

from .download import Downloader
from .utils import fail_custom_msg, LoggingHandler

class ExampleDownloader(Downloader):
    criteria = ...  # Iterates through these and extracts items from pages
    db_url = "postgresql://user:@localhost:port/"
    main_table = "example"

    def _init_urls(self):
        # Initialise variable urls
        self.url = f'...'
        self.search = f'{self.url}/...'
        self.items_url = f'{self.url}/...'

    async def get_refs_each(self, criterion, lastUpdate):
        """Get references"""
        try:
            ...
        except Exception as e:
            self.log.error(f'{e}')

    def process_item_data(self, db, ref, response):
        record = {}

        # Add items to record
        ...

        # Add to DB
        db.add_record(flatdict.FlatDict(record))


class ExampleDownloader(ExampleDownloader):
    db_name = "Example"


def download():
    ExampleDownloader().download()
