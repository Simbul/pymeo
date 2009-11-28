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
    
    def test_get_feed(self):
        feed = self.__pymeo.get_feed('videos.getLikes', {'user_id':2638277})
        self.__assert_feed_object(feed)
        self.assertEquals(feed.page, 1)
        self.assertEquals(feed.perpage, 20)
        self.assertEquals(feed.on_this_page, len(feed))
    
    def test_feed_iterate(self):
        feed = self.__pymeo.get_feed('videos.getLikes', {'user_id':2638277})
        i = 0
        check_ids = []
        for item in feed:
            self.assert_('id' in item)
            i += 1
            check_ids.append(item)
        
        # Check length
        self.assertEquals(i, len(feed))
        
        # Check replicability
        for item in feed:
            self.assert_('id' in item)
            self.assertEquals(item.id, check_ids.pop(0).id)
            i -= 1
        self.assertEquals(i, 0)
    
    def test_get_video(self):
        video = self.__pymeo.get_video(7545734)
        self.__assert_feed_item(video)
    
    
    def __assert_feed_object(self, feed):
        self.assert_(isinstance(feed, pymeo.PymeoFeed))
        self.assert_(hasattr(feed, 'on_this_page'))
        self.assert_(hasattr(feed, 'perpage'))
        self.assert_(hasattr(feed, 'page'))
        self.assert_(hasattr(feed, 'method'))
        self.assert_(hasattr(feed, 'params'))
    
    def __assert_feed_item(self, item):
        self.assert_(isinstance(item, pymeo.PymeoFeedItem))
    

if __name__ == '__main__':
    unittest.main()