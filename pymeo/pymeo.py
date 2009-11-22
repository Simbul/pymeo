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


import urllib2
import json
from oauth.oauth import *

class VimeoException(Exception):
    def __init__(self, code, message, explaination=None):
        Exception.__init__(self, code, message, explaination)
    
    def __str__(self):
        out = "%s: %s" % (self.args[0], self.args[1])
        if self.args[2] is not None:
            out += " (%s)" % self.args[2]
        return out
    

class PymeoFeedItem(object):
    def __init__(self, json):
        self.__entry = json
    
    def __getattr__(self, name):
        return self.__entry[name]
    

class PymeoFeed(object):
    def __init__(self, json_feed, method, params):
        json = json_feed.copy()
        self.on_this_page = int(json.pop('on_this_page'))
        self.total = int(json.pop('total'))
        self.perpage = int(json.pop('perpage'))
        self.page = int(json.pop('page'))
        
        self.method = method
        self.params = params
        
        self.__current = 0
        if len(json) == 1:
            (self.type, self.__entries) = json.popitem()
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.__current >= len(self.__entries):
            raise StopIteration
        else:
            self.__current += 1
            return PymeoFeedItem(self.__entries[self.__current-1])
    
    def is_last_page(self):
        """
            Return whether this is the last page.
        """
        return (self.page * self.perpage >= self.total)

# {u'stat': u'ok', u'generated_in': u'0.2642',
#  u'videos': {
    # u'on_this_page': u'2', u'total': u'2', u'perpage': u'50',
    # u'video': [
        # {u'upload_date': u'2009-11-11 05:58:15', u'title': u'Know Your Meme: Auto Tune (featuring "Weird Al" Yankovic)', u'privacy': u'anybody', u'is_hd': u'1', u'embed_privacy': u'anywhere', u'owner': u'243010', u'id': u'7545734'}, 
        # {u'upload_date': u'2009-10-17 05:53:00', u'title': u'IoT e Hardware Sociali (iCrocco)', u'privacy': u'anybody', u'is_hd': u'0', u'embed_privacy': u'anywhere', u'owner': u'807018', u'id': u'7112182'}
    # ], u'page': u'1'
#  }
# }

class Pymeo(OAuthConsumer):
    BASE_URL = "http://vimeo.com/api/rest/v2/"
    AUTH_URL = "http://vimeo.com/services/auth/"
    
    def __init__(self, c_key, c_secret):
        OAuthConsumer.__init__(self, c_key, c_secret)
        self.signature_method = OAuthSignatureMethod_HMAC_SHA1()
    
    def get_feed(self, method, params):
        """
            Get a feed of items returned from a specific method.
            
            @param method A string representing a Vimeo method
            @param params A dict of parameters for the method
        """
        json_res = self.function_call(method, params)
        for v in json_res.values():
            if isinstance(v, dict):
                return PymeoFeed(v, method, params)
        
        raise Error('The requested method cannot return a feed')
    
    def get_next_feed(self, feed):
        """
            Return the feed following the one passed as a parameter.
            
            The next feed is basically the next page of items.
            If there are no more pages, return None.
        """
        if feed.is_last_page():
            return None
        else:
            params = feed.params.copy()
            params['page'] = feed.page + 1
            return self.get_feed(feed.method, params)
    
    def function_call(self, method, params, base_url=None):
        if method[0:6] != "vimeo.":
            method = "vimeo." + method
        
        return self.request(method, params)
    
    def request(self, method, params, base_url=None):
        url = base_url or Pymeo.BASE_URL
        
        # Build the OAuth part of the request
        auth_req = OAuthRequest().from_consumer_and_token(
            oauth_consumer=self,
            http_url=url,
            parameters=params
        )
        auth_req.set_parameter('method', method)
        auth_req.set_parameter('format', 'json')
        auth_req.sign_request(self.signature_method, self, None)
        
        # Build actual HTTP Request
        req = urllib2.Request(auth_req.to_url())
        req.add_header("User-Agent", "pymeo/0.1")
        
        # Perform request
        out = []
        try:
            f = urllib2.urlopen(req)
            out = json.loads(f.read())
        except urllib2.URLError, e:
            print "urllib error", e, e.filename
        if 'err' in out:
            # Vimeo returned an error message -> raise an exception
            raise VimeoException(
                out['err']['code'],
                out['err']['msg'],
                out['err']['expl']
            )
        
        return out
        

class User(object):
    def __init__(self, username):
        self.__username = username
