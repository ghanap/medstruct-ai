from utils.database import init_db

TEST_DB = ':memory:'

def test_database_init():
    init_db(TEST_DB)
    # If no exception, it works
    assert True
