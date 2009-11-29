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
from ConfigParser import ConfigParser

from pymeo import pymeo
import mocks

# Comment the following line to run the test against the remote server
pymeo.urllib2.urlopen = mocks.dummy_urlopen

class AdvancedTest(unittest.TestCase):
    def setUp(self):
        # Setup advanced API
        self.consumer_secret = self.consumer_key = None
        
        try:
            config = ConfigParser()
            config.read('configuration')
            self.consumer_key = config.get('OAuth', 'consumer_key')
            self.consumer_secret = config.get('OAuth', 'consumer_secret')
        except:
            pass
        self.__pymeo = pymeo.Pymeo(self.consumer_key, self.consumer_secret)
    
    def test_advanced(self):
        self.assert_(self.__pymeo.is_advanced())
    
    def test_echo(self):
        resp = self.__pymeo.request_advanced('vimeo.test.echo')
        self.__assert_advanced_response(resp)
        self.assertEquals(resp['oauth_consumer_key'], self.consumer_key)
    
    def test_wrongauth(self):
        pymeo_wrong = pymeo.Pymeo("wrongkey", "wrongsecret")
        self.assertRaises(pymeo.VimeoException, pymeo_wrong.request_advanced, 'vimeo.test.echo')
    
    def test_request_single(self):
        resp = self.__pymeo.request_advanced('vimeo.people.getInfo', {'user_id': 2638277})
        self.__assert_advanced_response(resp)
        self.assert_('person' in resp)
        
        person = resp['person']
        self.assert_("id" in person)
        self.assert_("display_name" in person)
        self.assert_("is_staff" in person)
        self.assert_("is_plus" in person)
        self.assert_("location" in person)
        self.assert_("url" in person)
        self.assert_("profileurl" in person)
        self.assert_("videosurl" in person)
        self.assert_("number_of_videos" in person)
        self.assert_("number_of_videos_appears_in" in person)
        self.assert_("number_of_likes" in person)
        self.assert_("number_of_contacts" in person)
        self.assertEquals(person['id'], '2638277')
    
    def test_request_multi(self):
        resp = self.__pymeo.request_advanced('vimeo.videos.getLikes', {'user_id': 2638277})
        self.__assert_advanced_response(resp)
        self.assert_('videos' in resp)
        feed = resp['videos']
        self.__assert_json_feed(feed)
        self.assert_('video' in feed)
        self.assert_(isinstance(feed['video'], list))
    
    def test_get_feed(self):
        feed = self.__pymeo.get_feed('videos.getLikes', {'user_id':2638277})
        self.__assert_feed_object(feed)
        self.assertEquals(feed.page, 1)
        self.assertEquals(feed.perpage, 50)
        self.assertEquals(feed.on_this_page, len(feed))
    
    def test_get_video(self):
        video = self.__pymeo.get_video(7545734)
        self.__assert_feed_item(video)
        self.assertEquals(video.id, u'7545734')
        
        self.assert_(video.get_thumbnail('small').endswith('100.jpg'))
        self.assert_(video.get_thumbnail('medium').endswith('200.jpg'))
        self.assert_(video.get_thumbnail('large').endswith('640.jpg'))
        
        self.assert_(video.get_video_url().endswith('7545734'))
    
    def test_get_videos(self):
        video_feed = self.__pymeo.get_feed('videos.getLikes', {'user_id': '2638277'})
        self.__assert_feed_object(video_feed)
        for item in video_feed:
            self.__assert_video_item(item)
    
    def test_thumb_fallback(self):
        video = self.__pymeo.get_video(7545734)
        
        # This call returns the default image
        self.assert_('default' in video.get_thumbnail('huge'))
        
        # This call falls back on the 'large' size
        self.assert_(video.get_thumbnail('huge', vimeo_default=False).endswith('640.jpg'))
    
    def __assert_advanced_response(self, resp):
        self.assert_(isinstance(resp, dict))
        self.assert_("stat" in resp)
        self.assert_("generated_in" in resp)
    
    def __assert_json_feed(self, feed):
        self.assert_(isinstance(feed, dict))
        self.assert_('page' in feed)
        self.assert_('perpage' in feed)
        self.assert_('on_this_page' in feed)
    
    def __assert_feed_object(self, feed):
        self.assert_(isinstance(feed, pymeo.PymeoFeed))
        self.assert_(hasattr(feed, 'on_this_page'))
        self.assert_(hasattr(feed, 'perpage'))
        self.assert_(hasattr(feed, 'page'))
        self.assert_(hasattr(feed, 'method'))
        self.assert_(hasattr(feed, 'params'))
    
    def __assert_feed_item(self, item):
        self.assert_(isinstance(item, pymeo.PymeoFeedItem))
    
    def __assert_video_item(self, item):
        self.assert_(isinstance(item, pymeo.PymeoVideo), "Not an instance of PymeoVideo: found %s instead" % item.__class__.__name__)
    

if __name__ == '__main__':
    unittest.main()
