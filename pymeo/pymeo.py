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

class Pymeo(OAuthConsumer):
    BASE_URL = "http://vimeo.com/api/rest/v2/"
    AUTH_URL = "http://vimeo.com/services/auth/"
    
    def __init__(self, c_key, c_secret):
        OAuthConsumer.__init__(self, c_key, c_secret)
        self.signature_method = OAuthSignatureMethod_HMAC_SHA1()
    
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
        try:
            f = urllib2.urlopen(req)
            return json.loads(f.read())
        except urllib2.URLError, e:
            print "urllib error", e, e.filename
    

class User(object):
    def __init__(self, username):
        self.__username = username
