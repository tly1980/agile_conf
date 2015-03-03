#!/usr/bin/env python
import argparse
import os
import datetime


import yaml

import agile_conf

AP = argparse.ArgumentParser(description='An awesome app to compile configs.')
AP.add_argument('action', type=str, help='available actions are conf')
AP.add_argument('-m', '--modules', nargs='+', default=[], help='action')
AP.add_argument(
    '--conf', default=None, type=str, help='''Config for the build.
    If you don't specify it will try to lookup enviornment variable "AC_CONF".
    If it is not exists, it will fallback to conf.yaml in the working directory.
''')


def main(args):
    conf_path, conf = agile_conf.get_conf(args)
    prj = agile_conf.Project(os.getcwd(), conf)

    if args.action == 'create':
        print "please implement"

    elif args.action == 'build':
        print "build started %s ..." % prj.build_id()
        prj.build()
        print "build finished"

    elif args.action == 'where':
        print prj.dst_base_folder()
    elif args.action == 'id':
        print prj.build_id()
    elif args.action == 'new':
        conf['number'] += 1
        print "Build number +1 to %s updating file: %s" % (
            conf['number'],
            conf_path)
        with open(conf_path, 'wb') as f:
            conf['updated'] = datetime.datetime.now(
                ).strftime('%Y-%m-%d %H:%M:%S')
            cnt = yaml.dump(conf, default_flow_style=False)
            f.write(cnt)

if __name__ == '__main__':
    main(AP.parse_args())
