# Testing Example class
import asyncio
import copy
import flatdict
import pytest

from example import ExampleDownloader
from downloader_scraper.db import DB
from downloader_scraper.utils import NoNoneOrderedDict

# Setup class to test
cls = ExampleDownloader()


def test_item_get_store_retrieve():
    """Tests the item's whole lifecycle - getting, storing and retrieving."""
    # Initialise DB connection
    db = DB(db_url='sqlite:///:memory:')
    db.db.row_type = NoNoneOrderedDict

    # Test with the first item only
    resp = flatdict.FlatDict(cls.session.get(cls.items_url.format(1)).json())

    # Add item to the db (copy as lists modified in-place; not what we want)
    db.add_record(copy.copy(resp))

    # Insert into DB
    db.commit()

    # Retrieve and compare to original to ensure data integrity is maintained
    # specifically foreign keys
    record = list(db.retrieve_records())[0]

    # Ensure keys are identical
    assert sorted(record.keys()) == sorted(resp.keys())

    for items in resp:
        # Change the foreign items to match that of the retrieved records
        if type(resp[items]) == list:
            resp[items] = [
                dict(flatdict.FlatDict(item)) for item in resp[items]
            ]

            # Simplest way to check unordered lists items
            assert record[items] == resp[items] or \
                min([item in record[items] for item in resp[items]])
        else:
            # Check the keys against each other to ensure they are identical
            assert record[items] == resp[items]
