

from bottle import Bottle, route, run, template

app = Bottle()

def start_server(address='127.0.0.1', port=8080, debug=False):
    """Start the http server

    :param host:
    :param port:
    :param debug:
    :return:
    """

    run(host=address, port=port, reloader=debug, debug=debug)


@route('/')
def index():
    return template('<b>Hello {{name}}</b>!', name="AGS")



@route('/spec/ags4')
def ags4_spec():
    return template('<b>SPECCC {{name}}</b>!', name="AGS")
