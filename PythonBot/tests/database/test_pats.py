import unittest
from database import pats, common


class Commands(unittest.TestCase):
    def test_pats(self):
        self.r = pats.increment_pats(1, 2)
        print(self.r)

        common.get_table(pats.PAT_DATABASE, pats.PAT_TABLE).drop()
