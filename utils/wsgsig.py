import hashlib
import time
from urllib.parse import urlparse, unquote
 
import execjs
 
 
def get_sig(url):
    query = get_query(url)
    query_dict = query_string_to_map(query)
    map_string = sign_map_to_string(query_dict)
    return str(len(map_string)) + "&sig=" + encrypt_to_md5("R4doMFFeMNlliIWM" + map_string)
 
 
def get_query(url):
    parsed_url = urlparse(url)
    return parsed_url.query
 
 
def query_string_to_map(query_str):
    query_dict = {}
    try:
        for param in query_str.split('&'):
            if param:
                key, value = map(unquote, param.split('=', 1))
                query_dict[key + value] = ''
    except Exception as e:
        print(e)
    return query_dict
 
 
def sign_map_to_string(query_dict):
    try:
        sorted_params = sorted(query_dict.keys(), reverse=True)
        result = ''
        for param in sorted_params:
            if not param.startswith("__x_") and param.lower() != "wsgsig":
                result += param
                result += query_dict[param]
        return result
    except Exception as e:
        print(e)
 
 
def encrypt_to_md5(data):
    return hashlib.md5(data.encode()).hexdigest()
 
 
def get_wsgsig(content):
    js = """function i(t) {
            for (var e = "ABCDEFG0123456789abcdefgHIJKLMN+/hijklmnOPQRSTopqrstUVWXYZuvwxyz", n = "" + t, i = void 0, r = void 0, o = 0, a = ""; n.charAt(0 | o) || (e = "=",
            o % 1); a += e.charAt(63 & i >> 8 - o % 1 * 8)) {
                if ((r = n.charCodeAt(o += .75)) > 255)
                    throw new Error("'base64' failed: The string to be encoded contains characters outside of the Latin1 range.");
                i = i << 8 | r
            }
            return a
        }
        function r(t, e) {
            for (var n = [], i = 0; i < e.length; i++)
                n[i] = t[i % 4] ^ e.charCodeAt(i);
            return n = Array.prototype.slice.apply(t).concat(n),
            String.fromCharCode.apply(null, n)
        };
        function getWsgsig(T){
            return encodeURIComponent("dd03-" + i(r(new Uint8Array(new Uint32Array([Math.floor(4294967296 * Math.random())]).buffer), T)).replace(/=*$/, ""));
        };"""
    ctx = execjs.compile(js)
    result = ctx.call("getWsgsig", content)
    return result
 

def generate_wsgsig()->str:
    '''
    获取wsgsig
    '''
    timestamp = str(int(time.time()))
    url = 'https://dorado.xiaojukeji.com/usce-api/carlib/getAllSeriesByBrand?nginx_cors=false&_t=' + timestamp + '&city_id=1&usce_channel=24448&usce_sub_channel=127395&grade_type_id=7&is_hxz=0&brand_id=1115&cityid=1&cityId=1&city-id=1'
    sig = get_sig(url)
    content = 'ts=' + timestamp + '&v=1&os=web&av=02&kv=0000010001&vl=' + sig
    wsgsig = get_wsgsig(content)
    return wsgsig
 
if __name__ == '__main__':
    # timestamp = str(int(time.time()))
    # url = 'https://dorado.xiaojukeji.com/usce-api/carlib/getAllSeriesByBrand?nginx_cors=false&_t=' + timestamp + '&city_id=1&usce_channel=24448&usce_sub_channel=127395&grade_type_id=7&is_hxz=0&brand_id=1115&cityid=1&cityId=1&city-id=1'
    # sig = get_sig(url)
    # content = 'ts=' + timestamp + '&v=1&os=web&av=02&kv=0000010001&vl=' + sig
    # wsgsig = get_wsgsig(content)
    # print(wsgsig)
    # print()
    # print(url + '&wsgsig=' + wsgsig)
    print(generate_wsgsig())
 
 
