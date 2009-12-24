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

import urllib2
try:
    import json
except ImportError:
    import simplejson as json
import urlparse

from pymeo.pymeo import Pymeo

class MockFileObject(object):
    def __init__(self, json):
        self.__json = json
    
    def read(self):
        # return json.dumps(self.__json)
        return self.__json
    
if hasattr(urlparse, 'parse_qs'):
    pymeo_parse_qs = urlparse.parse_qs
else:
    import cgi
    pymeo_parse_qs = cgi.parse_qs

def dummy_urlopen(req):
    """
        Dummy function simulating a server response.
    """
    if not isinstance(req, urllib2.Request):
        raise Exception('Method dummy_urlopen requires a Request parameter')
    
    url = req.get_full_url()
    if url.startswith(Pymeo.BASE_URL):
        # Advanced API
        query = pymeo_parse_qs(urlparse.urlparse(url).query)
        
        if query['oauth_consumer_key'][0] == 'wrongkey':
            j = '{' \
                '"stat": "fail",' \
                '"generated_in": "0.0001",' \
                '"err": {"msg": "Invalid API Key", "code": "100", "expl": "The API key passed was not valid"}' \
            '}'
        else:
            method = query['method'][0]
            if method == 'vimeo.test.echo':
                j = '{"stat":"ok","generated_in":"0.0001"'
                for k,v in query.iteritems():
                    j += ',"%s":"%s"' % (k, v[0])
                j += '}'
            elif method == 'vimeo.people.getInfo':
                j = '{"generated_in":"0.0442","stat":"ok","person":{"id":"2638277","is_plus":"0","is_staff":"0","username":"simbul","display_name":"Simbul","location":"","url":[""],"number_of_contacts":"0","number_of_uploads":"0","number_of_likes":"3","number_of_videos":"0","number_of_videos_appears_in":"0","profileurl":"http:\/\/vimeo.com\/simbul","videosurl":"http:\/\/vimeo.com\/simbul\/videos"}}'
            elif method == 'vimeo.videos.getLikes':
                j = '{"generated_in":"0.1255","stat":"ok","videos":{'\
                    '"on_this_page":"3","page":"1","perpage":"50","total":"3","video":['\
                    '{"embed_privacy":"anywhere","id":"7764570","is_hd":"1","liked_on":"2009-11-26 16:51:34","owner":"1696981","privacy":"anybody","title":"Title1","upload_date":"2009-11-22 20:14:47"},'\
                    '{"embed_privacy":"anywhere","id":"7545734","is_hd":"1","liked_on":"2009-11-15 05:00:40","owner":"243010","privacy":"anybody","title":"Title2","upload_date":"2009-11-11 05:58:15"},'\
                    '{"embed_privacy":"anywhere","id":"7112182","is_hd":"0","liked_on":"2009-11-15 04:54:49","owner":"807018","privacy":"anybody","title":"Title3","upload_date":"2009-10-17 05:53:00"}'\
                    ']}}'
            elif method == 'vimeo.videos.getInfo':
                j = '{"generated_in":"0.3395","stat":"ok","video":['\
                    '{"embed_privacy":"anywhere","id":"7545734","is_hd":"1","is_transcoding":"0","privacy":"anybody","title":"Title","caption":"Caption",'\
                    '"description":"Desc","upload_date":"2009-11-11 05:58:15","number_of_likes":"385","number_of_plays":"24003","number_of_comments":"24","width":"640","height":"360","duration":"352",'\
                    '"owner":{"display_name":"Rocketboom","id":"243010","is_plus":"1","is_staff":"0","profileurl":"http:\/\/vimeo.com\/rocketboom","realname":"Rocketboom","username":"rocketboom","videosurl":"http:\/\/vimeo.com\/rocketboom\/videos","portraits":{"portrait":[{"height":"30","width":"30","_content":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_30.jpg"},{"height":"75","width":"75","_content":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_75.jpg"},{"height":"100","width":"100","_content":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_100.jpg"},{"height":"300","width":"300","_content":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_300.jpg"}]}},'\
                    '"tags":{"tag":[{"author":"243010","id":"18448553","normalized":"autotune","url":"http:\/\/vimeo.com\/tag:autotune","_content":"auto tune"},{"author":"243010","id":"18448554","normalized":"internet","url":"http:\/\/vimeo.com\/tag:internet","_content":"internet"},{"author":"243010","id":"18448555","normalized":"meme","url":"http:\/\/vimeo.com\/tag:meme","_content":"meme"},{"author":"243010","id":"18448556","normalized":"music","url":"http:\/\/vimeo.com\/tag:music","_content":"music"},{"author":"243010","id":"18448557","normalized":"mashup","url":"http:\/\/vimeo.com\/tag:mashup","_content":"mashup"},{"author":"243010","id":"18448558","normalized":"remix","url":"http:\/\/vimeo.com\/tag:remix","_content":"remix"}]},'\
                    '"cast":{"member":[{"display_name":"Rocketboom","id":"243010","role":"","username":"rocketboom"},{"display_name":"Jamie Dubs","id":"193251","role":"","username":"jamiew"},{"display_name":"Ellie","id":"305256","role":"","username":"user305256"},{"display_name":"yatta","id":"669","role":"","username":"yatta"},{"display_name":"Chris Menning","id":"1269540","role":"","username":"user1269540"},{"display_name":"Andrew Kornhaber","id":"700512","role":"","username":"kornhaber"},{"display_name":"Barry Pousman","id":"844566","role":"","username":"barrypousman"},{"display_name":"Brad Kim","id":"2054079","role":"","username":"user2054079"},{"display_name":"waymoby","id":"134966","role":"","username":"weirdal"}]},'\
                    '"urls":{"url":[{"type":"video","_content":"http:\/\/vimeo.com\/7545734"},{"type":"group","_content":"http:\/\/vimeo.com\/groups\/26994\/videos\/7545734"}]},'\
                    '"thumbnails":{"thumbnail":[{"height":"75","width":"100","_content":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_100.jpg"},{"height":"150","width":"200","_content":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_200.jpg"},{"height":"360","width":"640","_content":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_640.jpg"},{"height":"720","width":"1280","_content":"http:\/\/bitcast.vimeo.com\/vimeo\/thumbnails\/defaults\/default.300x400.jpg"}]}}]}'
            else:
                raise NotImplementedError('Method %s not supported by the mock urlopen method' % method)
        
    elif url.startswith(Pymeo.SIMPLE_URL):
        # Simple API
        params = url.replace(Pymeo.SIMPLE_URL, "").split("/")
        if params[0] == 'video':
            v_id = params[1].replace('.json', '')
            j = '[{"id":"7545734","title":"Title","description":"Desc","url":"http:\/\/vimeo.com\/7545734","upload_date":"2009-11-11 05:58:15","thumbnail_small":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_100.jpg","thumbnail_medium":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_200.jpg","thumbnail_large":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/327\/289\/32728953_640.jpg","user_name":"Rocketboom","user_url":"http:\/\/vimeo.com\/rocketboom","user_portrait_small":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_30.jpg","user_portrait_medium":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_75.jpg","user_portrait_large":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_100.jpg","user_portrait_huge":"http:\/\/images.vimeo.com\/11\/28\/69\/112869861\/112869861_300.jpg","stats_number_of_likes":"385","stats_number_of_plays":"24003","stats_number_of_comments":24,"duration":"352","width":"640","height":"360","tags":"auto tune, internet, meme, music, mashup, remix"}]'
        elif params[0] == 'activity':
            pass
        elif params[0] == 'group':
            pass
        elif params[0] == 'channel':
            pass
        elif params[0] == 'album':
            pass
        else:
            # User
            if params[1].startswith('info') and params[0] == '2638277':
                j = '{"id":"2638277","display_name":"Simbul","created_on":"2009-11-15 04:46:39","is_staff":"0","is_plus":"0","location":"","url":"","bio":"","profile_url":"http:\/\/vimeo.com\/simbul","videos_url":"http:\/\/vimeo.com\/simbul\/videos","total_videos_uploaded":0,"total_videos_appears_in":0,"total_videos_liked":3,"total_contacts":0,"total_albums":0,"total_channels":0,"portrait_small":"http:\/\/bitcast.vimeo.com\/vimeo\/portraits\/defaults\/d.30.jpg","portrait_medium":"http:\/\/bitcast.vimeo.com\/vimeo\/portraits\/defaults\/d.75.jpg","portrait_large":"http:\/\/bitcast.vimeo.com\/vimeo\/portraits\/defaults\/d.100.jpg","portrait_huge":"http:\/\/bitcast.vimeo.com\/vimeo\/portraits\/defaults\/d.300.jpg"}'
            elif params[1].startswith('likes') and params[0] == '2638277':
                j = '[{"id":"7764570","title":"Title1","description":"Description1","url":"http:\/\/vimeo.com\/7764570","upload_date":"2009-11-22 20:14:47","thumbnail_small":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_100.jpg","thumbnail_medium":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_200.jpg","thumbnail_large":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_640.jpg","user_name":"brandon moza","user_url":"http:\/\/vimeo.com\/user1696981","user_portrait_small":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_30.jpg","user_portrait_medium":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_75.jpg","user_portrait_large":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_100.jpg","user_portrait_huge":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_300.jpg","stats_number_of_likes":"919","stats_number_of_plays":"17725","stats_number_of_comments":141,"duration":"229","liked_on":"2009-11-26 16:51:34","width":"640","height":"360","tags":"sometag"},'\
                '{"id":"7545734","title":"Title1","description":"Description1","url":"http:\/\/vimeo.com\/7764570","upload_date":"2009-11-22 20:14:47","thumbnail_small":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_100.jpg","thumbnail_medium":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_200.jpg","thumbnail_large":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_640.jpg","user_name":"brandon moza","user_url":"http:\/\/vimeo.com\/user1696981","user_portrait_small":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_30.jpg","user_portrait_medium":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_75.jpg","user_portrait_large":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_100.jpg","user_portrait_huge":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_300.jpg","stats_number_of_likes":"919","stats_number_of_plays":"17725","stats_number_of_comments":141,"duration":"229","liked_on":"2009-11-26 16:51:34","width":"640","height":"360","tags":"sometag"},'\
                '{"id":"7112182","title":"Title1","description":"Description1","url":"http:\/\/vimeo.com\/7764570","upload_date":"2009-11-22 20:14:47","thumbnail_small":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_100.jpg","thumbnail_medium":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_200.jpg","thumbnail_large":"http:\/\/ts.vimeo.com.s3.amazonaws.com\/343\/836\/34383667_640.jpg","user_name":"brandon moza","user_url":"http:\/\/vimeo.com\/user1696981","user_portrait_small":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_30.jpg","user_portrait_medium":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_75.jpg","user_portrait_large":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_100.jpg","user_portrait_huge":"http:\/\/ps.vimeo.com.s3.amazonaws.com\/164\/164487_300.jpg","stats_number_of_likes":"919","stats_number_of_plays":"17725","stats_number_of_comments":141,"duration":"229","liked_on":"2009-11-26 16:51:34","width":"640","height":"360","tags":"sometag"}]'
    
    out = MockFileObject(j)
    return out