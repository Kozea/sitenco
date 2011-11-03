#!/usr/bin/env python

import argparse
import sitenco

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('project', nargs='?', help='project name')
    arg_parser.add_argument('--cache', action='store_true', help='use cache')
    args = arg_parser.parse_args()
    sitenco.PROJECT_NAME = getattr(args, 'project')
    if not args.cache:
        sitenco.cache.set_cache = lambda cache, key, value: None
    sitenco.app.run(host='0.0.0.0', debug=True)
