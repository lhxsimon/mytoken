import asyncio
import platform
from sanic import Sanic
from sanic.response import json
from ctypes import cdll, c_char_p
from mytoken import get_params, fetch_url
from time import time

contact_info = "获取无限时版本, 请联系 lhxsimon@gmail.com"


def create_app():
    '''
    create sanic app and load libtoken
    '''

    # load libtoken.so
    dll_file = "libtoken.so"

    if platform.system() == "Darwin":
        dll_file = "libtoken_darwin.so"
    elif platform.system() == "Linux":
        dll_file = 'libtoken_linux.so'
    else:
        print("Cannot support system: ", platform.system())
        exit(1)

    libtoken = cdll.LoadLibrary("./assets/{}".format(dll_file))
    libtoken.GetKey.argtypes = [c_char_p, c_char_p]
    libtoken.GetKey.restype = c_char_p

    # check license
    with open("./license/license.dat", "r", encoding='utf-8') as f:
        license = f.read()

    check_license(license, libtoken)

    # create app
    app = Sanic(__name__)

    # load html page
    with open("./assets/index.html", "r", encoding='utf-8') as f:
        html = f.read()

    return app, libtoken, license, html


def check_license(license, libtoken):
    if license is None or license == "":
        print("License data error!")
        exit(1)

    license_time = license.split(":")[0]
    timestamp = int(time())

    if timestamp > int(license_time):
        print("License time out")
        exit(1)

    timestamp = str(timestamp).encode('utf-8')
    license = license.encode('utf-8')
    code = libtoken.GetKey(timestamp, license).decode("utf-8")

    if code.startswith('error'):
        print("License libtoken.so error")
        exit(1)


def run_server(app, host, port, debug=True):
    '''
    Use asyncio loop run sanic server
    '''
    loop = asyncio.get_event_loop()
    server = app.create_server(host=host, port=port, debug=debug)
    asyncio.ensure_future(server)
    loop.run_forever()


async def forward_request(request, path, libtoken, license):
    params = await get_params(request, libtoken, license)

    if params['code'].startswith("error"):
        resp = {
            'contact': contact_info,
            'status': 1,
            'error': 'License 错误',
            'data': None,
        }
        return json(resp)

    if path == 'currency/refreshprice':
        resp = await fetch_url(path, params, "POST")
    else:
        resp = await fetch_url(path, params)

    parse_resp = parse_response(path, resp)
    final_resp = {'contact': contact_info}
    final_resp.update(parse_resp)
    return json(final_resp)


def parse_response(path, resp_data):
    if resp_data is None:
        return {
            'status': 1,
            'error': '获取 {} 错误!'.format(path),
            'data': None,
        }

    if resp_data['code'] != 0:
        return {
            'status': 1,
            'error': 'Mytoken 内部错误: {}'.format(resp_data['message']),
            'data': None,
        }

    return {
        'status': 0,
        'error': None,
        'data': resp_data['data'],
    }
