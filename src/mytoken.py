from aiohttp import ClientSession
from time import time

mytoken_id = "fcfa9e7e826d73248b99a6591cc4f142"
mytoken_ua = "GoIco/1.5.0 (iPhone; iOS 11.2.5; Scale/3.00)"
mytoke_baseurl = "http://api.lb.mytoken.org/"


async def get_mytoken_code(libtoken, timestamp, license):
    '''
    Invoke libtoken.so
    '''
    timestamp = str(timestamp)
    timestamp = timestamp.encode("utf-8")
    license = license.encode("utf-8")
    return libtoken.GetKey(timestamp, license).decode("utf-8")


async def get_params(request, libtoken, license):
    '''
    Generate request params
    '''
    current_time = int(time())
    code = await get_mytoken_code(libtoken, current_time, license)

    params = request.raw_args
    params['code'] = code
    params['mytoken'] = mytoken_id
    params['timestamp'] = current_time
    return params


async def fetch_url(url, params, method='GET'):
    '''
    Fetch url data
    '''
    req_url = mytoke_baseurl + url

    async with ClientSession(headers={'User-Agent': mytoken_ua}) as session:

        if method == 'GET':
            req_func = session.get
        else:
            req_func = session.post

        async with req_func(req_url, params=params) as r:
            if r.status != 200:
                return None
            resp = await r.json()
            return resp
