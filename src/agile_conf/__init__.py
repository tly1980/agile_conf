#!/usr/bin/env python
import argparse
import re
import os
import os.path
from collections import namedtuple
import json
import datetime
import sys
import shutil
import fnmatch

import yaml
import jinja2

ENV_ARGS_CFG = 'AGC_CONF'
ENV_ARGS_BOIL = 'AGC_BOIL'


def load_version():
    path = os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)),
        'VERSION.txt')
    with open(path) as f:
        return f.read().strip()

VERSION = load_version()


def aws_userdata(arg_lst):
    lines = []
    path = os.path.join(*arg_lst)
    with open(path) as f:
        for l in f:
            lines.append("%s\n" % l.strip())

    return json.dumps({
        'Fn::Base64': {
            'Fn::Join': [
                '',
                lines
            ]
        }
    }, indent=4)


def template_env(*tpl_folder_lst):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(tpl_folder_lst)
    )
    env.filters['jsonify'] = json.dumps
    env.filters['yamlify'] = yaml.dump
    env.filters['aws_userdata'] = aws_userdata
    return env


class Project(object):
    def __init__(self, proj_folder, build_conf):
        self.proj_folder = proj_folder
        self.modules = []
        self.list_modules()
        self.the_config = {'conf': build_conf}

        self.load_config()

    def list_modules(self):
        '''has to run before config'''
        (fullpath, folders, files) = next(
            os.walk(self.proj_folder))
        self.modules = [
            f for f in folders if f[0] not in ['_', '.']
        ]

    def load_config(self):
        self.load_config_from_project()

        for m in self.modules:
            self.load_config_by_module(m)

    def load_config_from_project(self):
        tpl_env = template_env(self.proj_folder)
        tpl = tpl_env.get_template('project.yaml')

        txt_conf = tpl.render(conf=self.the_config['conf'])
        self.the_config['project'] = yaml.load(txt_conf)

    def load_config_by_module(self, m):
        tpl_env = template_env(
            os.path.join(self.proj_folder, m))
        tpl = tpl_env.get_template('module.yaml')
        txt_conf = tpl.render(**self.the_config)
        self.the_config[m] = yaml.load(txt_conf)

    def build(self):
        for m in self.modules:
            dst_folder = os.path.join(
                self.dst_base_folder(), m)
            self._build(True, m, dst_folder)

        if os.path.isdir(os.path.join(self.proj_folder, '_script')):
            self._build(False, '_script', self.dst_base_folder())

    def build_id(self, seperator='/'):
        return seperator.join([
            str(self.the_config['conf']['name']),
            str(self.the_config['conf']['number'])
        ])

    def dst_base_folder(self):
        return os.path.join(
            self.proj_folder,
            '_builds',
            str(self.the_config['conf']['name']),
            str(self.the_config['conf']['number'])
        )

    def dst_base_tmp_folder(self):
        return os.path.join(
            self.proj_folder,
            '_builds',
            '.tmp',
            str(self.the_config['conf']['name']),
            str(self.the_config['conf']['number'])
        )

    def _build(self, is_module, m, dst_folder):
        src_folder = os.path.join(self.proj_folder, m)
        if is_module:
            print "building: %s (module)" % m
        else:
            print "building: %s" % m


        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        if is_module:
            # 1. produce the module.yaml
            dst_module_cfg = os.path.join(dst_folder, 'module.yaml')
            with open(dst_module_cfg, 'wb') as f:
                yaml.dump(self.the_config[m], f, default_flow_style=False)

        tpl_env = template_env(self.proj_folder, src_folder)
        fullpath, folders, files = next(os.walk(src_folder))

        params = dict(self.the_config)
        params['_BUILD_DST_FOLDER'] = dst_folder

        if is_module:
            params.update(self.the_config[m])

        files = sorted(files)
        files_tpl = [
            fname for fname in files if fname.endswith('.tpl')]
        files_cp = [
            fname for fname in files if fname not in files_tpl]

        if is_module:
            _ignores = self.the_config[m].get('_ignores', [])

            for p in _ignores:
                files_cp = [
                    f for f in files_cp if not fnmatch.fnmatch(f, p)]


        for fname in files_cp:
            if fname not in ('module.yaml', ):
                src_path = os.path.join(src_folder, fname)
                dst_path = os.path.join(dst_folder, fname)
                shutil.copyfile(src_path, dst_path)
                print "%s copied from (%s)" % (fname, src_path)

        for fname in files_tpl:
            path = os.path.join(src_folder, fname)
            dst_path = os.path.join(dst_folder, fname[:-4])
            # read the template
            with open(path) as f:
                tpl = tpl_env.get_template(fname)
                cnt = tpl.render(params)
                # render it to dst folder
                with open(dst_path, 'wb') as f2:
                    f2.write(cnt)
                    print "%s <== [%s]" % (
                        dst_path[len(dst_folder)+1:], fname)

        # empty line make it easier to see
        print "" 


def get_conf(args_confpath):
    conf_path = os.environ.get(ENV_ARGS_CFG) if not args_confpath else args_confpath

    if not conf_path:
        sys.exit("""No config is provided. Please specify it in 
enviornment variable %s, or as option argument --conf.""" % ENV_ARGS_CFG)

    if not os.path.isfile(conf_path):
        sys.exit("The config file %s is invalid." % conf_path)

    try:
        with open(conf_path) as f:
            return conf_path, yaml.load(f)
    except:
        sys.exit("failed to open build conf file: %s" % conf_path)


def retire():
    pass

