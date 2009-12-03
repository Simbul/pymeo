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
import re

class VimeoException(Exception):
    def __init__(self, code, message, explaination=None):
        Exception.__init__(self, code, message, explaination)
    
    def __str__(self):
        out = "%s: %s" % (self.args[0], self.args[1])
        if self.args[2] is not None:
            out += " (%s)" % self.args[2]
        return out
    

class PymeoDict(dict):
    def __getattr__(self, name):
        if isinstance(self[name], dict):
            return PymeoDict(self[name])
        return self[name]
    

class PymeoFeedItem(PymeoDict):
    def to_video(self):
        return PymeoVideo(self)
    

class PymeoVideo(PymeoFeedItem):
    def get_thumbnail(self, size='medium', vimeo_default=True):
        """
            Return a thumbnail for the specified size.
            
            When vimeo_default is False, the method will try to avoid
            returning the Vimeo default thumbnail, possibly falling back
            to a smaller size.
            
            @param size Either small, medium, large or huge
            @param vimeo_default A boolean
        """
        if not size in ('small', 'medium', 'large', 'huge'):
            raise KeyError('Size "%s" is not a viable option' % size)
        
        sizes = [
            {'name': 'small', 'width': 100},
            {'name': 'medium', 'width': 200},
            {'name': 'large', 'width': 640},
            {'name': 'huge', 'width': 1280},
        ]
        
        thumb = None
        falling_back = False
        for size_item in reversed(sizes):
            if size_item['name'] == size or falling_back:
                falling_back = True
                thumb = self.__get_thumb_for_width(size_item['width'])
                if thumb is not None:
                    if vimeo_default: break
                    elif (re.search(r'/default[^/]+$', thumb) is None): break
        
        return thumb or ""
    
    def get_video_url(self):
        for url in self['urls']['url']:
            if url['type'] == 'video':
                return url['_content']
    
    def get_tags_string(self):
        out = []
        for tag in self['tags']['tag']:
            out.append(tag['_content'])
        
        return ", ".join(out)
    
    def __get_thumb_for_width(self, width):
        for thumb in self['thumbnails']['thumbnail']:
            if thumb['width'] == unicode(width):
                return thumb['_content']
    

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
            (self.type, entries) = json.popitem()
            if isinstance(entries, list):
                self.__entries = entries
            elif isinstance(entries, dict):
                self.__entries = [entries]
            else:
                raise Exception('Cannot construct PymeoFeed')
        
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
            entry = self.__entries[self.__current-1]
            if 'upload_date' in entry:
                return PymeoVideo(entry)
            else:
                return PymeoFeedItem(entry)
    

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
        return self.get_feed_item('videos.getInfo', {'video_id': video_id}).to_video()
    
    def get_feed_item(self, method, params):
        """
            Return a single feed item.
            
            If the request provides a feed with more than a single item, only
            the first one is returned.
        """
        feed = self.get_feed(method, params)
        for item in feed:
            return item
    
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
                if 'page' in v:
                    # The response contains a feed (with page number and the likes)
                    return PymeoFeed(v, method, params)
                else:
                    # The response contains an item
                    return PymeoFeed(
                        {
                            u'on_this_page': 1,
                            u'perpage': 20,
                            u'page': 1,
                            u'total': 1,
                            u'items': [v],
                        },
                        method, params
                    )
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
                u'items': self.__map_simple_to_advanced(json),
            }
        }
        return json_res
    
    def __map_simple_to_advanced(self, simple_json):
        """
            Map a simple json response to an advanced one.
            
            Return a list, both if the parameter is a list and if it's a
            single item.
        """
        if not isinstance(simple_json, list):
            simple_json = [simple_json]
        
        out = []
        for item in simple_json:
            advanced_item = {}
            for k,v in item.iteritems():
                if k in mappings:
                    # Transform according to mapping
                    transform = mappings[k]
                    if callable(transform):
                        # Apply transformation function
                        transform(k, v, advanced_item)
                    else:
                        # Just change the key in the dict
                        advanced_item[transform] = unicode(v)
                else:
                    # Keep as-is
                    advanced_item[k] = unicode(v)
            out.append(advanced_item)
                    
        return out
    
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
    

# {simple: advanced}
def map_thumbnails(simple_key, simple_value, advanced_dict):
    if not 'thumbnails' in advanced_dict:
        advanced_dict['thumbnails'] = {}
    if not 'thumbnail' in advanced_dict['thumbnails']:
        advanced_dict['thumbnails']['thumbnail'] = []
    if simple_key == 'thumbnail_small':
        thumb = {u'width': u'100', u'height': u'75', u'_content': simple_value}
    elif simple_key == 'thumbnail_medium':
        thumb = {u'width': u'200', u'height': u'150', u'_content': simple_value}
    elif simple_key == 'thumbnail_large':
        thumb = {u'width': u'640', u'height': u'360', u'_content': simple_value}
    
    advanced_dict['thumbnails']['thumbnail'].append(thumb)

def map_urls(simple_key, simple_value, advanced_dict):
    if not 'urls' in advanced_dict:
        advanced_dict['urls'] = {}
    if not 'url' in advanced_dict['urls']:
        advanced_dict['urls']['url'] = []
    if simple_key == 'url':
        url = {u'type': u'video', u'_content': simple_value}
    
    advanced_dict['urls']['url'].append(url)

def map_portraits(simple_key, simple_value, advanced_dict):
    if not 'owner' in advanced_dict:
        advanced_dict['owner'] = {}
    if not 'portraits' in advanced_dict['owner']:
        advanced_dict['owner']['portraits'] = {}
    if not 'portrait' in advanced_dict['owner']['portraits']:
        advanced_dict['owner']['portraits']['portrait'] = []
    
    if simple_key == 'user_portrait_small':
        portrait = {u'width': u'30', u'height': u'30', u'_content': simple_value}
    elif simple_key == 'user_portrait_medium':
        portrait = {u'width': u'75', u'height': u'75', u'_content': simple_value}
    elif simple_key == 'user_portrait_large':
        portrait = {u'width': u'100', u'height': u'100', u'_content': simple_value}
    elif simple_key == 'user_portrait_huge':
        portrait = {u'width': u'300', u'height': u'300', u'_content': simple_value}
    
    advanced_dict['owner']['portraits']['portrait'].append(portrait)

def map_tags(simple_key, simple_value, advanced_dict):
    if not 'tags' in advanced_dict:
        advanced_dict['tags'] = {}
    if not 'tag' in advanced_dict['tags']:
        advanced_dict['tags']['tag'] = []
    
    if simple_key == 'tags':
        for tag in simple_value.split(', '):
            advanced_dict['tags']['tag'].append(
                {u'_content': tag}
            )

def map_owner(simple_key, simple_value, advanced_dict):
    if not 'owner' in advanced_dict:
        advanced_dict['owner'] = {}
    
    if simple_key == 'user_url':
        advanced_dict['owner']['profileurl'] = simple_value
    elif simple_key == 'user_name':
        advanced_dict['owner']['display_name'] = simple_value


mappings = {
    'stats_number_of_comments': 'number_of_comments',
    'stats_number_of_plays': 'number_of_plays',
    'stats_number_of_likes': 'number_of_likes',
    'thumbnail_small': map_thumbnails,
    'thumbnail_medium': map_thumbnails,
    'thumbnail_large': map_thumbnails,
    'url': map_urls,
    'user_portrait_small': map_portraits,
    'user_portrait_medium': map_portraits,
    'user_portrait_large': map_portraits,
    'user_portrait_huge': map_portraits,
    'tags': map_tags,
    'user_url': map_owner,
    'user_name': map_owner,
}
class User(object):
    def __init__(self, username):
        self.__username = username
