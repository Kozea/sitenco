#!/usr/bin/env python

import argparse
import sitenco

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('project', nargs='?', help='project name')
    sitenco.PROJECT_NAME = getattr(arg_parser.parse_args(), 'project')
    sitenco.app.run(host='0.0.0.0', debug=True)

