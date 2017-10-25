#encoding=utf-8
import urllib2
import traceback
import jsonpickle

from utils.LogUtils import *

class HttpUtils:

    @staticmethod
    def get(url, headers, charset):
        response = None
        try:
            req = urllib2.Request(url, headers=headers)
#	    req.add_header('Referer', 'http://q.10jqka.com.cn/gn/detail/code/300008/')
	    response = urllib2.urlopen(req)
            buf = response.read()
	    return buf.decode(charset)
        except Exception, e:
	    if hasattr(e, 'code'):
		LogUtils.info('get url = %s, return_code=%s, reason = %s' % (url, e.code, e.reason))
		if e.code == 404:
		    return ''
            return None
        finally:
            if response is not None:
                response.close()


if __name__ == '__main__':
    headers = {}
#    headers['Referer'] = 'http://q.10jqka.com.cn/gn/detail/code/300008/'
    url = 'http://q.10jqka.com.cn/gn/detail/code/300157/'
    print HttpUtils.get(url, headers, 'gbk')
