import sys
sys.path.append('.')
sys.path.append('..')

import unittest
from ConfigParser import ConfigParser

from pymeo import pymeo
import mocks

# Comment the following line to run the test against the remote server
pymeo.urllib2.urlopen = mocks.dummy_urlopen

class CoherencyTest(unittest.TestCase):
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
        self.__pymeo_advanced = pymeo.Pymeo(self.consumer_key, self.consumer_secret)
        self.__pymeo_simple = pymeo.Pymeo()
    
    # def test_get_user(self):
    #     user_simple = self.__pymeo_simple.get_feed_item('people.getInfo', {'user_id':2638277})
    #     user_advanced = self.__pymeo_advanced.get_feed_item('people.getInfo', {'user_id':2638277})
    #     self.__assert_feed_items_equal(user_advanced, user_simple)
    
    def test_get_video(self):
        json_simple = self.__pymeo_simple.function_call('videos.getInfo', {'video_id': 7545734})
        json_advanced = self.__pymeo_advanced.function_call('videos.getInfo', {'video_id': 7545734})
        self.__assert_json_is_subset(json_advanced['video'][0], json_simple['feed']['items'][0])
    
    def __assert_json_is_subset(self, superset, subset, parent_key=""):
        """
            Assert that a json variable is a subset of another variable.
            
            This means that the superset contains every key/value in the
            subset, and it could contain more.
        """
        for k, v in subset.iteritems():
            self.assert_(k in superset, 'superset has no key "%s" (%s)' % (k, parent_key))
            if isinstance(v, dict):
                self.__assert_json_is_subset(superset[k], v, k)
            elif isinstance(v, list):
                # TODO: manage this case
                pass
            else:
                self.assertEquals(v, superset[k])

if __name__ == '__main__':
    unittest.main()
