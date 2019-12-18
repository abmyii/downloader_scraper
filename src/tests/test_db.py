from src.db import DB


def test_column_reference():
    k = 'column_which_has_a_really_long_name_longer_than_sixty_four_characters'

    db = DB('sqlite:///:memory:', main_tbl_name="test")
    db.add_record({'id': 1, k: 0})
    db.commit()

    assert k in list(db.retrieve_records())[0].keys()
