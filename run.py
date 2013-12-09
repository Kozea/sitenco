#!/usr/bin/env python3

import argparse
import sitenco

try:
    import wdb.ext
except ImportError:
    pass
else:
    wdb.ext.add_w_builtin()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('project', nargs='?', help='project name')
    arg_parser.add_argument('--cache', action='store_true', help='use cache')
    arg_parser.add_argument('--port', action='store', type=int,
                            default=5000, help='server port')
    args = arg_parser.parse_args()
    sitenco.PROJECT_NAME = getattr(args, 'project')

    try:
        import wdb.ext
    except ImportError:
        pass
    else:
        sitenco.app.wsgi_app = wdb.ext.WdbMiddleware(
            sitenco.app.wsgi_app, start_disabled=True)
    if not args.cache:
        sitenco.cache.set_cache = lambda cache, key, value: None
    sitenco.app.run(host='0.0.0.0', debug=True, port=args.port)
