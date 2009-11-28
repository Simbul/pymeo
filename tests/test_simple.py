import sys
sys.path.append('.')
sys.path.append('..')

import unittest

from pymeo import pymeo
import mocks

# Comment the following line to run the test against the remote server
pymeo.urllib2.urlopen = mocks.dummy_urlopen

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Setup simple API
        self.__pymeo = pymeo.Pymeo()
    
    def test_simple_request_single(self):
        resp = self.__pymeo.request_simple(2638277, 'info')
        self.assert_(isinstance(resp, dict))
        self.assert_("id" in resp)
        self.assert_("display_name" in resp)
        self.assert_("created_on" in resp)
        self.assert_("is_staff" in resp)
        self.assert_("is_plus" in resp)
        self.assert_("location" in resp)
        self.assert_("url" in resp)
        self.assert_("bio" in resp)
        self.assert_("profile_url" in resp)
        self.assert_("videos_url" in resp)
        self.assert_("total_videos_uploaded" in resp)
        self.assert_("total_videos_appears_in" in resp)
        self.assert_("total_videos_liked" in resp)
        self.assert_("total_contacts" in resp)
        self.assert_("total_albums" in resp)
        self.assert_("total_channels" in resp)
        self.assert_("portrait_small" in resp)
        self.assert_("portrait_medium" in resp)
        self.assert_("portrait_large" in resp)
        self.assert_("portrait_huge" in resp)
        self.assertEquals(resp['id'], '2638277')
    
    def test_simple_request_multi(self):
        resp = self.__pymeo.request_simple(2638277, 'likes')
        self.assert_(isinstance(resp, list))
        for item in resp:
            self.assert_("id" in item)
            self.assert_("url" in item)

    
if __name__ == '__main__':
    unittest.main()