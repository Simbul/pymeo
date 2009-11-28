import sys
sys.path.append('.')
sys.path.append('..')

import urllib2
import json
import urlparse

from pymeo.pymeo import Pymeo

class MockFileObject(object):
    def __init__(self, json):
        self.__json = json
    
    def read(self):
        # return json.dumps(self.__json)
        return self.__json
    

def dummy_urlopen(req):
    """
        Dummy function simulating a server response.
    """
    if not isinstance(req, urllib2.Request):
        raise Exception('Method dummy_urlopen requires a Request parameter')
    
    url = req.get_full_url()
    if url.startswith(Pymeo.BASE_URL):
        # Advanced API
        query = urlparse.parse_qs(urlparse.urlparse(url).query)
        
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
        
    elif url.startswith(Pymeo.SIMPLE_URL):
        # Simple API
        params = url.replace(Pymeo.SIMPLE_URL, "").split("/")
        if params[0] == 'video':
            pass
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
            
    
    
    # j = {u'stat': u'ok', u'generated_in': u'0.2642',
    #  u'videos': {
    #     u'on_this_page': u'2', u'total': u'2', u'perpage': u'50',
    #     u'video': [
    #         {u'upload_date': u'2009-11-11 05:58:15', u'title': u'Know Your Meme: Auto Tune (featuring "Weird Al" Yankovic)', u'privacy': u'anybody', u'is_hd': u'1', u'embed_privacy': u'anywhere', u'owner': u'243010', u'id': u'7545734'}, 
    #         {u'upload_date': u'2009-10-17 05:53:00', u'title': u'IoT e Hardware Sociali (iCrocco)', u'privacy': u'anybody', u'is_hd': u'0', u'embed_privacy': u'anywhere', u'owner': u'807018', u'id': u'7112182'}
    #     ], u'page': u'1'
    #  }
    # }
    
    out = MockFileObject(j)
    return out