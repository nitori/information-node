
import informationnode.tcp.server
import unittest

class TCPTest(unittest.TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_main(self):
        server = informationnode.tcp.server.TCPServer()
        self.assertEqual(1, 2)

