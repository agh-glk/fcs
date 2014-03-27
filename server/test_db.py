from linkdb import BerkeleyBTreeLinkDB
from key_policy_module import SimpleKeyPolicyModule
import os
import datetime
import time


class TestDataBase(object):

    def setup(self):
        self.links_db = BerkeleyBTreeLinkDB("test_db", SimpleKeyPolicyModule)

    def test_one_in_base(self):
        _link = "www.test.com"
        self.links_db.add_link(_link, 1, 1)
        assert self.links_db.get_link() is not None

    def test_get_from_empty_base(self):
        assert self.links_db.get_link() is None

    def test_empty_queue(self):
        _link = "www.test.com"
        self.links_db.add_link(_link, 1, 1)
        self.links_db.get_link()
        assert self.links_db.get_link() is None

    def test_priority_set(self):
        _link = "www.test.com"
        self.links_db.add_link(_link, 1, 8)
        _details = self.links_db.get_details(_link)
        assert _details[2] == '8'

    def test_depth_set(self):
        _link = "www.test.com"
        self.links_db.add_link(_link, 6, 4)
        _details = self.links_db.get_details(_link)
        assert _details[0] == '6'

    def test_is_in_base(self):
        _link = "www.test.com"
        self.links_db.add_link(_link, 1, 1)
        assert self.links_db.is_in_base(_link) is True

    def test_is_not_in_base(self):
        _link1 = "www.test.com"
        _link2 = "www.test22222.com"
        self.links_db.add_link(_link1, 1, 1)
        assert self.links_db.is_in_base(_link2) is False

    def test_best_priority_in_queue1(self):
        '''
        Kolejnosc liter.
        '''
        _link = "www.aaa.com"
        self.links_db.add_link("www.abc.com", 1, 3)
        self.links_db.add_link(_link, 1, 1)
        assert self.links_db.get_link() == _link

    def test_best_priority_in_queue2(self):
        """
        Dluzszy link.
        """
        _link = "www.aaa.com"
        self.links_db.add_link(_link, 1, 1)
        self.links_db.add_link("www.aaa.com/aaaa/aa", 1, 3)
        assert self.links_db.get_link() == _link

    def test_best_priority_in_queue3(self):
        """
        Link krotszy, ale kolejnosc liter.
        """
        _link = "www.aaa.com"
        self.links_db.add_link(_link, 1, 1)
        self.links_db.add_link("www.zz.com", 1, 3)
        assert self.links_db.get_link() == _link

    def test_best_priority_in_queue4(self):
        """
        Priorytet.
        """
        _link = "www.aaa.com"
        self.links_db.add_link(_link, 1, 1)
        _link2 = "www.zz.com"
        self.links_db.add_link("www.zz.com", 4, 3)
        assert self.links_db.get_link() == _link2

    def test_best_priority_in_queue5(self):
        """
        Priorytety o roznych liczbach cyfr.
        """
        _link = "www.zzz.com"
        self.links_db.add_link(_link, 12, 1)
        self.links_db.add_link("www.aaa.com", 4, 3)
        assert self.links_db.get_link() == _link

    def test_best_priority_in_queue6(self):
        """
        Priorytety o roznych liczbach cyfr.
        """
        _link = "www.zzz.com"
        self.links_db.add_link(_link, 12, 1)
        self.links_db.add_link("www.aaa.com/asasf/34", 4, 3)
        assert self.links_db.get_link() == _link

    def test_set_as_fetched(self):
        _link = "www.zzz.com"
        self.links_db.add_link(_link, 12, 1)
        _t0 = datetime.datetime.now()
        self.links_db.set_as_fetched(_link)
        _details = self.links_db.get_details(_link)
        assert _t0 < datetime.datetime.strptime(_details[1], "%Y-%m-%d %H:%M:%S.%f")

    def test_feedback(self):
        _link = "www.zzz.com"
        self.links_db.add_link(_link, 12, 1)
        self.links_db.feedback(_link, 5)
        _details = self.links_db.get_details(_link)
        assert _details[0] == '5'

    def test_feedback_correct_keys(self):
        _link = "www.zzz.com"
        self.links_db.add_link(_link, 12, 1)
        self.links_db.feedback(_link, 5)
        assert self.links_db.policy_module.generate_key(_link, 5) in self.links_db.priority_queue


    def teardown(self):
        self.links_db.close()
        os.remove("test_db")