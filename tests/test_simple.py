# -*- coding: utf-8 -*-

# Copyright © 2009 Alessandro Morandi (email : webmaster@simbul.net)
#
# This file is part of pymeo.
# 
# pymeo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pymeo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with pymeo.  If not, see <http://www.gnu.org/licenses/>.

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
    
    def test_feed_extend(self):
        feed = self.__pymeo.get_feed('videos.getLikes', {'user_id':2638277})
        
        items = []
        items.extend({'title': item.title} for item in feed)
        
        self.assertEquals(len(items), len(feed))
        i = 0
        for item in feed:
            self.assertEquals(items[i]['title'], item.title)
            i += 1
    
    def test_get_video(self):
        video = self.__pymeo.get_video(7545734)
        self.__assert_video_item(video)
        
        self.assert_(video.get_thumbnail('small').endswith('100.jpg'))
        self.assert_(video.get_thumbnail('medium').endswith('200.jpg'))
        self.assert_(video.get_thumbnail('large').endswith('640.jpg'))
        
        self.assert_(video.get_video_url().endswith('7545734'))
        
        tags = video.get_tags_string()
        self.assert_(isinstance(tags, unicode))
        self.assert_(len(tags) > 0)
        
        # Huge falls back to large
        self.assert_(video.get_thumbnail('huge').endswith('640.jpg'))
    
    def test_get_videos(self):
        video_feed = self.__pymeo.get_feed('videos.getLikes', {'user_id': '2638277'})
        self.__assert_feed_object(video_feed)
        for item in video_feed:
            self.__assert_video_item(item)
    
    def test_thumb_fallback(self):
        video = self.__pymeo.get_video(7545734)
        
        # This call falls back on the 'large' size
        self.assert_(video.get_thumbnail('huge').endswith('640.jpg'))
        
        # This call falls back on the 'large' size too
        self.assert_(video.get_thumbnail('huge', vimeo_default=False).endswith('640.jpg'))
    
    def test_tags(self):
        video = self.__pymeo.get_video(7545734)
        
        tags = ["auto tune", "internet", "meme", "music", "mashup", "remix"]
        self.assertEquals(len(video.tags.tag), len(tags))
        for t in video.tags.tag:
            self.assert_(t['_content'] in tags, 'Tag "%s" not found' % t['_content'])
        
        self.assertEquals(video.get_tags_string(), ", ".join(tags))
    
    
    def __assert_feed_object(self, feed):
        self.assert_(isinstance(feed, pymeo.PymeoFeed))
        self.assert_(hasattr(feed, 'on_this_page'))
        self.assert_(hasattr(feed, 'perpage'))
        self.assert_(hasattr(feed, 'page'))
        self.assert_(hasattr(feed, 'method'))
        self.assert_(hasattr(feed, 'params'))
    
    def __assert_feed_item(self, item):
        self.assert_(isinstance(item, pymeo.PymeoFeedItem), "Not an instance of PymeoFeedItem: found %s instead" % item.__class__.__name__)
    
    def __assert_video_item(self, item):
        self.assert_(isinstance(item, pymeo.PymeoVideo), "Not an instance of PymeoVideo: found %s instead" % item.__class__.__name__)
    

if __name__ == '__main__':
    if pymeo.urllib2.urlopen == mocks.dummy_urlopen:
        print "Running tests against mock Vimeo server"
    unittest.main()