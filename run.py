#!/usr/bin/env python
"""
Piati: build a site upon IATI data.
Usage:
    run.py serve [--port=<number>] [--host=<string>] [options]
    run.py static [--port=<number>] [--host=<string>] [options]
    run.py fetch [options]
    run.py build [options]
    run.py i18n (extract|update|compile) [options]
    run.py shell [options]

Examples:
    python run.py serve --port 5432 --debug
    python run.py build

Options:
    -h --help           print this message and exit
    --port=<number>     optionnaly pass a server port [default: 5665]
    --host=<string>     optionnaly pass a server port [default: 127.0.0.1]
    --settings=<path>   optionnaly pass a settings path
    --debug             optionnaly run in debug mode
"""
import os
import sys

from docopt import docopt
from flask_frozen import Freezer
from flask.ext.babel import Babel
from babel.messages.frontend import CommandLineInterface

from piati.app import app, load_data, DATA
from piati.helpers import fetch_remote_data, get_data_filepath, fetch_exchange_rates


if __name__ == '__main__':

    args = docopt(__doc__, version='Piati 0.1')

    def get_option(option, default=None):
        return args.get('--{0}'.format(option), os.environ.get(option.upper()))

    app.config.from_object('piati.settings.default')
    if os.environ.get('PIATI_SETTINGS'):
        app.config.from_envvar('PIATI_SETTINGS')
    if args["--settings"]:
        app.config.from_object(args['--settings'])
    freezer = Freezer(app)
    babel = Babel(app)
    if not args['fetch']:
        load_data()

    if args['serve']:
        app.run(
            debug=get_option('debug'),
            port=int(args['--port']),
            host=args['--host']
        )
    elif args['fetch']:
        for name, url in app.config['DATA'].items():
            filepath = get_data_filepath(app, name)
            fetch_remote_data(url, filepath)
        fetch_exchange_rates(app)
    elif args['build']:
        if not DATA:
            sys.exit("No data, nothing to build.")
        freezer.freeze()
    elif args['static']:
        freezer.serve(
            debug=get_option('debug'),
            port=int(args['--port']),
            host=args['--host']
        )
    elif args['i18n']:
        if args['extract']:
            babel_args = ['', 'extract', '-F', 'babel.cfg', '-o', 'messages.pot', '.']
        elif args['compile']:
            babel_args = ['', 'compile', '-d', 'piati/translations']
        elif args['update']:
            babel_args = ['', 'update', '-i', 'messages.pot', '-d', 'piati/translations']
        CommandLineInterface().run(babel_args)
    elif args['shell']:
        import IPython
        IPython.embed()
