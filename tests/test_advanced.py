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
    
    def __assert_advanced_response(self, resp):
        self.assert_(isinstance(resp, dict))
        self.assert_("stat" in resp)
        self.assert_("generated_in" in resp)
    
    def __assert_json_feed(self, feed):
        self.assert_(isinstance(feed, dict))
        self.assert_('page' in feed)
        self.assert_('perpage' in feed)
        self.assert_('on_this_page' in feed)
    

if __name__ == '__main__':
    unittest.main()