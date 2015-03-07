#!/usr/bin/env python
"""agile_conf command line tool.

Usage:
  agc create (<bo_name> <prj_name> | --list) [--bo_repo=<path>]
  agc build [--conf=<path>]
  agc inspect [--conf=<path>] [--yaml]
  agc next [--conf=<path>]
  agc retire [<id>] [--conf=<path>]
  agc id [--conf=<path>]
  agc where [--conf=<path>]
  agc info [--conf=<path>]


Options:
  -h --help         Show this screen.
  --version         Show version.
  --conf=<path>     Config for the build.
                    If it is not specified,
                    will use enviornment variable AGC_CONF
  --bo_repo=<path>  Path for the boilerplate repository.
                    If it is not specified,
                    This can also be specified in enviornment
  --list            List available projects

Commands:
  create            Create project from boilerplate

"""
from docopt import docopt

import argparse
import os
import datetime
import os
import subprocess
import sys
import json
import shutil

import yaml

import agile_conf


def inspect(args, project):
    if not args.get('--yaml'):
        print "%s" % json.dumps(project.the_config, indent=2)
    else:
        print yaml.dump(project.the_config, default_flow_style=False)
    sys.exit(0)


def retire(project, conf_path, conf_number=None):
    conf_name = project.the_config['conf']['name']
    if not conf_number:
        conf_number = str(project.the_config['conf']['number'])

    conf_id = os.path.join(
        project.the_config['conf']['name'], conf_number)

    retired_base_dir = os.path.join(
        project.proj_folder, '_retired')

    src_path = os.path.join(
        project.proj_folder, '_builds', conf_name, conf_number)

    dst_path = os.path.join(
        retired_base_dir, conf_name, conf_number)

    if not os.path.exists(src_path):
        sys.exit("Conf %s wasn't built." % conf_id)

    if os.path.exists(dst_path):
        sys.exit(
            '''{dst_path} is already existed. 
Please move {src_path} to {retired_base_dir} manually.
Make sure you name it differently.
'''.format(dst_path=dst_path, src_path=src_path,
        retired_base_dir=retired_base_dir)
    )

    print "retiring %s " % conf_id
    shutil.move(src_path, dst_path)
    print """%s conf_id is marked retired.
Make sure you've run the destroy script as well.""" % conf_id
    print "To undo this. you can run:\n  mv %s %s " % (dst_path, src_path)

    if int(conf_number) == int(project.the_config['conf']['number']):
        print "As you retired the corruent build, will increase the current build number"
        auto_next(project.the_config['conf'], conf_path)


def auto_next(conf, conf_path):
    conf['number'] += 1
    print "Conf number increased to [%s]\nupdating file: %s" % (
        conf['number'],
        conf_path)
    with open(conf_path, 'wb') as f:
        conf['updated'] = datetime.datetime.now(
            ).strftime('%Y-%m-%d %H:%M:%S')
        cnt = yaml.dump(conf, default_flow_style=False)
        f.write(cnt)


def boil_base(boil_base_arg):
    if not boil_base_arg:
        boil_base = os.environ.get(
            agile_conf.ENV_ARGS_BOIL)
    else:
        boil_base=boil_base_arg

    if not boil_base:
        msg = """Please specify your boilerplate repo using
--bo_repo or enviornment variable: ENV_ARGS_BOIL.

If you don't have a local boilerplate repo, you can clone
https://github.com/tly1980/agile_conf_boilplate.git to start with."""
        sys.exit(msg)

    if boil_base.startswith('~'):
        boil_base = os.path.expanduser(boil_base)

    if not boil_base or not os.path.isdir(boil_base):
        sys.exit(
            "Boilerplate repository folder: %s is not a valid folder." % boil_base)

    return os.path.abspath(boil_base)


def create(args):
    boil_name = args['<bo_name>']
    prj_name = args['<prj_name>']
    is_list = args['--list']

    boil_base_path = boil_base(args['--bo_repo'])

    if is_list:
        r = os.walk(boil_base_path)
        loc, dirs, files = r.next()
        for d in dirs:
            if not d.startswith('.'):
                print(d)
        return

    dst_path = os.path.join(os.getcwd(), prj_name)

    src_path = os.path.join(boil_base_path, boil_name)

    if os.path.exists(dst_path):
        sys.exit(
            "%s already exists. Please remove it or specify another project name other than: %s." % (
                dst_path, prj_name)
            )
    print """\
creating project: %s
using boilerplate: %s""" % (prj_name, src_path)
    shutil.copytree(src_path, dst_path)


def dp_main():
    args = docopt(__doc__, version=agile_conf.VERSION)

    if args.get('create'):
        create(args)
        return

    conf_path, conf = agile_conf.get_conf(args['--conf'])
    prj = agile_conf.Project(os.getcwd(), conf)

    if args.get('info'):
        print "conf=%s" % conf_path
        print "boilerplate_repo=%s" % conf_path
        return


    if args.get('inspect'):
        print "with [conf=%s]" % conf_path
        inspect(args, prj)
    elif args.get('build'):
        print "with [conf=%s] " % conf_path
        print "build started %s ... [%s]" % (
            prj.build_id(), prj.dst_base_folder())

        prj.build()
        print "build finished"
    elif args.get('id'):
        print prj.build_id()
    elif args.get('where'):
        print prj.dst_base_folder()
    elif args.get('next'):
        auto_next(conf, conf_path)
    elif args.get('retire'):
        retire(prj, conf_path, args.get('<id>'))


if __name__ == '__main__':
    dp_main()
