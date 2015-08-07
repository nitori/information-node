
can_use_postgres = True
try:
    import psycopg2
except ImportError:
    can_use_postgres = False

class PostgresStorageDriver(object):
    def __init__(self, node_folder):
        pass

    @staticmethod
    def available(self):
        if not can_use_postgres:
            return "psycopg2 not available, postgres storage driver "+\
                "cannot be used"
        return True

    def create_item(self, item_identifier):

    def delete_item(self, item_identifier):

    def get_item_chunk_count(self, item_identifier):
         

    def get_item_chunk(self, item_identifier, chunk_no):

    def set_item_chunk(self, item_identifier, chunk_no):

    def crop_item(self, item_identifier, chunks):


