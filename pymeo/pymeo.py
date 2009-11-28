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
        self.__current = 0
    
    def __getattr__(self, name):
        return self.__entry[name]
    
    def to_video(self):
        return PymeoVideo(self.__entry)
    
    def __repr__(self):
        return unicode(self.__entry)
    
    def __iter__(self):
        self.__current = 0
        return self
    
    def next(self):
        if self.__current >= len(self.__entry):
            raise StopIteration
        else:
            self.__current += 1
            return self.__entry.keys()[self.__current]

class PymeoVideo(PymeoFeedItem):
    pass
    

class PymeoFeed(object):
    def __init__(self, json_feed, method, params):
        json = json_feed.copy()
        self.on_this_page = int(json.pop('on_this_page'))
        self.perpage = int(json.pop('perpage'))
        self.page = int(json.pop('page'))
        
        if 'total' in json:
            self.total = int(json.pop('total'))
        else:
            self.total = None
        
        self.method = method
        self.params = params
        
        self.__current = 0
        if len(json) == 1:
            (self.type, self.__entries) = json.popitem()
    
    def __len__(self):
        return len(self.__entries)
    
    def __iter__(self):
        self.__current = 0
        return self
    
    def next(self):
        if self.__current >= len(self.__entries):
            raise StopIteration
        else:
            self.__current += 1
            return PymeoFeedItem(self.__entries[self.__current-1])
    
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
    """
        This class is a wrapper for Vimeo APIs.
        
        It wraps both simple and advanced APIs, even though the interface is
        based on the advanced API only.
        When the class is missing the consumer key and the consumer secret,
        it falls back automatically to the simple API. Otherwise the advanced
        API is used.
    """
    BASE_URL = "http://vimeo.com/api/rest/v2/"
    AUTH_URL = "http://vimeo.com/services/auth/"
    SIMPLE_URL = 'http://vimeo.com/api/v2/'
    
    def __init__(self, c_key=None, c_secret=None):
        OAuthConsumer.__init__(self, c_key, c_secret)
        self.signature_method = OAuthSignatureMethod_HMAC_SHA1()
    
    def is_advanced(self):
        """
            Return whether the instance is based on the advanced API.
            
            An instance not based on the advanced API will use the simple API.
        """
        return (self.key and self.key is not None and \
            self.secret and self.secret is not None)
    
    def get_video(self, video_id):
        feed = self.get_feed('videos.getInfo', {'video_id': video_id})
        for item in feed:
            return item.to_video()
    
    def get_feed(self, method, params):
        """
            Get a feed of items returned from a specific method.
            
            Return None when the feed is empty.
            
            @param method A string representing a Vimeo method
            @param params A dict of parameters for the method
        """
        json_res = self.function_call(method, params)
        
        if json_res is None:
            return None
        
        for v in json_res.values():
            if isinstance(v, dict):
                # The response contains a feed (with page number and the likes)
                return PymeoFeed(v, method, params)
            elif isinstance(v, list):
                # The response contains a single item (e.g. a video)
                return PymeoFeed(
                    {
                        u'on_this_page': 1,
                        u'perpage': 20,
                        u'page': 1,
                        u'total': 1,
                        u'items': v,
                    },
                    method, params
                )
        
        raise Exception('The requested method cannot return a feed')
    
    def get_next_feed(self, feed):
        """
            Return the feed following the one passed as a parameter.
            
            The next feed is basically the next page of items.
            If there are no more pages, return None.
        """
        if feed.total is not None and (feed.page * feed.perpage >= feed.total):
            # It was an advanced feed: we can tell if it's the last one
            #  without making any call
            return None
        else:
            params = feed.params.copy()
            params['page'] = feed.page + 1
            return self.get_feed(feed.method, params)
    
    def function_call(self, method, params, base_url=None):
        if method[0:6] != "vimeo.":
            method = "vimeo." + method
        
        if self.is_advanced():
            json_res = self.request_advanced(method, params)
        else:
            json_res = self.translate_simple_call(method, params)
        return json_res
    
    def translate_simple_call(self, method, params, base_url=None):
        """
            Translate an advanced call to a simple one.
        """
        context = identifier = request = None

        if method == 'vimeo.people.getInfo':
            identifier = params['user_id']
            request = 'info'
        elif method == 'vimeo.videos.getLikes':
            identifier = params['user_id']
            request = 'likes'
        elif method == 'vimeo.videos.getUploaded':
            identifier = params['user_id']
            request = 'videos'
        elif method == 'vimeo.videos.getInfo':
            context = 'video'
            identifier = params['video_id']
        elif method == 'vimeo.videos.getAppearsIn':
            identifier = params['user_id']
            request = 'appears_in'
        else:
            raise NotImplementedError('Method %s has not been implemented yet' % method)
        
        if 'page' in params:
            query = { 'page': params['page'] }
        else:
            query = None
        json = self.request_simple(
            context=context,
            identifier=identifier,
            request=request,
            query=query
        )
        
        if len(json) == 0:
            # No results
            return None
        
        if 'page' in params:
            page = params['page']
        else:
            page = 1
        
        json_res = {
            u'stat': u'ok-simple',
            u'feed': {
                u'on_this_page': len(json),
                u'perpage': 20,
                u'page': page,
                u'items': json,
            }
        }
        return json_res
    
    def request_advanced(self, method, params=None, base_url=None):
        url = base_url or Pymeo.BASE_URL
        
        if params is None:
            params = []
        
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
            raise Exception('Could not perform request: %s' % e.filename)
        if 'err' in out:
            # Vimeo returned an error message -> raise an exception
            raise VimeoException(
                out['err']['code'],
                out['err']['msg'],
                out['err']['expl']
            )
        
        return out
    
    def request_simple(self, identifier, request=None, context=None, query=None, base_url=None):
        """
            Perform a Simple API request.

            This will call a URL such as (for example)
            http://vimeo.com/api/v2/activity/someuser/user_did.json?page=1
            
            The output of the method will be a dict in this form:
            {'stat': '...', 'generated_in': '...', 'item_or_list': ...}

            @param context The context of the request, e.g. "activity"
            @param identifier The id for the request, e.g. "username"
            @param request The type of request, e.g. "user_did"
            @param query A dict representing a query to append, e.g {'page':1}
            @return A dict representing the response
        """
        url = base_url or Pymeo.SIMPLE_URL

        if context is not None:
            url += context + "/"

        url += str(identifier)
        if request is not None:
            url += "/" + request
        url += ".json"
        
        if query is not None:
            q = "?"
            for k, v in query.iteritems():
                q += "%s=%s&" % (k, v)
            url += q

        # Build actual HTTP Request
        req = urllib2.Request(url)
        req.add_header("User-Agent", "pymeo/0.1")

        # Perform request
        out = []
        try:
            f = urllib2.urlopen(req)
            out = json.loads(f.read())
        except urllib2.URLError, e:
            raise Exception('Could not perform request: %s' % e.filename)

        return out
    

class User(object):
    def __init__(self, username):
        self.__username = username
