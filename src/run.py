#!/usr/bin/env python3
from sanic import response
from sanic.exceptions import abort
from utils import create_app, run_server, forward_request

app, libtoken, license, index_html = create_app()


@app.route("/")
async def index(request):
    return response.html(index_html)


@app.route('/favicon.ico')
async def favicon(request):
    abort(404)


@app.route('/<path:[^/].*?>')
async def forward(request, path):
    return await forward_request(request, path, libtoken, license)


if __name__ == '__main__':
    run_server(app, '0.0.0.0', 8000, False)
