#!/usr/bin/env python
import argparse
import os
import datetime
import os
import subprocess
import sys

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


DEFAULT_CONF='''
boilerplate_repo: {bo_repo}
'''


def prepare_ag_conf(
        repo_path='https://github.com/tly1980/agile_conf_boilplate.git'):
    def prepare_repo(repo_location):
        return subprocess.call(
            ['git', 'clone', repo_path, repo_location])

    home_folder = os.path.expanduser('~/.agile_conf')
    if not os.path.isdir(home_folder):
        print "home folder wasn't created, about to create one."
        os.mkdir(home_folder)

        cfg_path = os.path.join(home_folder, 'conf.yaml')
        bo_repo = os.path.join(home_folder, 'bo_repo')
        with open(cfg_path, 'wb') as f:
            f.write(
                DEFAULT_CONF.format(bo_repo=bo_repo)
            )

        ret = prepare_repo(bo_repo)
        if ret != 1:
            sys.exit("Failed to clone repository: %s" % repo_path)


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
