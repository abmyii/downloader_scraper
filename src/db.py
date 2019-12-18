import dataset
import flatdict
import re

from collections import OrderedDict
from dataset.util import index_name, normalize_column_name


class DB:
    def __init__(self, db_url, db_name='', main_tbl_name=''):
        # Connect to database
        self.db = dataset.connect(f"{db_url}{db_name}", autocreate_db=True)
        self.tables = OrderedDict()  # Contains tables data
        self.main_tbl_name = main_tbl_name

    def table_add(self, table_name, items):
        if not self.tables.get(table_name, False):
            # Create table if it doesn't exist
            self.tables[table_name] = OrderedDict()

        # Convert to a list if not already one
        if not type(items) == list:
            items = [items]

        # Add item(s) to table dictionary.
        for item in items:
            for key in item:
                if len(key) > 63:
                    # Add key if not already present
                    self.db['__col_ref'].upsert(dict(name=key), 'name')

                    # Get key id
                    ref_id = self.db['__col_ref'].find_one(name=key)['id']
                    chars = int((60 - len(str(ref_id))) / 2)
                    new_key = f'{key[:chars]}·{key[-chars:]}#{ref_id}'

                    # https://stackoverflow.com/a/4406521
                    item[new_key] = item.pop(key)

            # Use id as key. Overwriting rather than duplication will occur.
            self.tables[table_name][item['id']] = item

    def add_record(self, record):
        """
        Adds a record to the DB - automatically splits foreign values, ect.
        To be run from an async function.
        """
        # Process item's values into relevant tables/formats
        # Lists are symbolic of foreign items.
        foreign = [item for item in record.items() if type(item[1]) == list]
        for name, items in foreign:
            # Add items to their relative table after flattening them
            # Has to be dicts with an id as added to a new table and referenced
            table_data = [
                flatdict.FlatDict(item, dict_class=OrderedDict)
                for item in items
            ]
            self.table_add(name, table_data)

            # Set key to name of foreign table for retrieve function to detect.
            record[name] = str([item['id'] for item in items])

        # Item is now the stripped down version (with FKs). Add to main table.
        self.table_add(self.main_tbl_name, record)

    def commit(self):
        """Add data to DB"""
        for name in self.tables:  # Key is the table name
            # Get or create tables
            table = self.db.create_table(name, primary_id="id")  # id is the PK

            # Add table's data to it
            table.upsert_many(self.tables[name].values(), ['id'])

        # Commit changes to DB
        self.db.commit()

    def search(self, table, terms={}):
        # https://stackoverflow.com/a/12118700
        terms = {k: v for k, v in terms.items() if v or v == 0}

        results = table.find(**terms)
        return results, table.count(**terms)

    def retrieve_records(self, search_terms={}, count=False):
        results = self.search(self.db[self.main_tbl_name], search_terms)
        records_gen = self.process_records(results[0])
        return (records_gen, results[1]) if count else records_gen

    def process_records(self, results):
        for record in results:
            # Using record.items() prevents modifying record
            items = [item for item in record.items()]
            for key, value in items:
                if len(key) > 60:  # Check for abbreviated names
                    # Check if it has a reference id
                    ref_id = re.findall(r'#(\d+)$', key)
                    if ref_id:
                        # Substitute with full-length name
                        name = self.db['__col_ref'].find_one(
                            id=int(ref_id[0])
                        )['name']

                        # https://stackoverflow.com/a/4406521
                        record[name] = record.pop(key)

                # Relational items identified by start = '[' and end = ']'
                if type(value) == str and re.match(r'^\[.*\]$', value):
                    # Find integer ids
                    ids = [int(i) for i in re.findall(r'(\d+)', value)]

                    # Get items into that key
                    record[key] = [i for i in list(self.db[key].find(id=ids))]

            # Yield modified record
            yield record
