#!/usr/bin/env python
import subprocess
import os
import unittest
import cStringIO as StringIO
import tempfile
import shutil
import json


import yaml

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        'src')
)

PROJECT_BASE_PATH = os.path.abspath(
    os.path.dirname(__file__))

os.environ["PATH"] = SRC_PATH + os.pathsep + os.environ["PATH"]


def run(working_path, *args):
    with tempfile.TemporaryFile() as f:
        os.chdir(working_path)
        ret = subprocess.call(args, stdout=f)
        f.flush()
        f.seek(0)
        return ret, "%s" % f.read()


def run_project(prj_name, *args):
    prj_path = os.path.join(PROJECT_BASE_PATH, prj_name)
    return run(prj_path, *args)

DEFAULT_PROD_YAML = '''
name: prod
number: 1
updated: '2015-01-01 00:00:00'
'''

CMD="main.py"

class Prj1Test(unittest.TestCase):
    def setUp(self):
        self.prj_name = 'prj1'
        self.prj_path = os.path.join(
            PROJECT_BASE_PATH, self.prj_name)

        with open(os.path.join(self.prj_path, 'prod.yaml'), 'wb') as f:
            f.write(DEFAULT_PROD_YAML)

        self.build_path = os.path.join(self.prj_path, '_builds')
        shutil.rmtree(self.build_path, True)

    def test_0new(self):
        ret, conf_id = run_project(
            self.prj_name,
            CMD, 'id', '--conf', 'prod.yaml')
        self.assertEqual(conf_id.strip(), 'prod/1')

        ret, stdout = run_project(
            self.prj_name,
            CMD, 'next', '--conf', 'prod.yaml')

        self.assertEqual(ret, 0)

        self.assertEqual(
            stdout,
            "Conf number increased to [2]\nupdating file: prod.yaml\n")

        ret, conf_id = run_project(
            self.prj_name,
            CMD, 'id', '--conf', 'prod.yaml')
        self.assertEqual(conf_id.strip(), 'prod/2')

    def test_build(self):
        ret, stdout = run_project(
            self.prj_name,
            CMD, 'build', '--conf', 'prod.yaml')
        self.assertEqual(ret, 0)
        self.assertEqual(
            stdout, """\
with [conf=prod.yaml] 
build started prod/1 ... [{prj_path}/_builds/prod/1]
building: m1 (module)
b_can_copy copied from ({prj_path}/m1/b_can_copy)
run.sh <== [run.sh.tpl]

build finished\n""".format(prj_path=self.prj_path))

        m1_path = os.path.join(self.prj_path, '_builds', 'prod', '1', 'm1', 'module.yaml')

        with open(m1_path) as f:
            m1 = yaml.load(f)
            self.assertEqual(m1, {
                '_ignores': ['*.not_copy', 'should_not_be_copy'],
                'name': 'awesome_project-prod-1'
            })

    def test_folder_structure(self):
        '''
        testing the folder structure, also for module _ignores
        '''
        ret, stdout = run_project(
            self.prj_name,
            CMD, 'build', '--conf', 'prod.yaml')

        flist = list(os.walk(
            os.path.join(self.prj_path, '_builds', 'prod')))
        flist_should = [
            (
                os.path.join(self.prj_path, '_builds', 'prod'),
                ['1'],
                []
            ),

            (
                os.path.join(self.prj_path, '_builds', 'prod', '1'),
                ['m1'],
                []
            ),

            (
                os.path.join(self.prj_path, '_builds', 'prod', '1', 'm1'),
                [],
                ['b_can_copy', 'module.yaml', 'run.sh']
            ),

        ]

        self.assertEqual(
            flist_should, flist)

        self.assertEqual(stdout, """\
with [conf=prod.yaml] 
build started prod/1 ... [{prj_path}/_builds/prod/1]
building: m1 (module)
b_can_copy copied from ({prj_path}/m1/b_can_copy)
run.sh <== [run.sh.tpl]

build finished\n""".format(prj_path=self.prj_path))

    @unittest.skip("fix it later.")
    def test_inspect(self):
        '''
        testing the folder structure, also for module _ignores
        '''
        ret, stdout = run_project(
            self.prj_name,
            CMD, 'inspect', '--conf', 'prod.yaml')
        cnt = '\n'.join(stdout.split('\n')[1:])
        d = json.loads(cnt)
        self.assertEqual(
            d, {
                "project": {
                "decription": "awesome_decription",
                "_executable": [
                "*.sh",
                "*.py"
            ],
            "name": "awesome_project",
            "_varient": "prod uat"
          },
          "m1": {
            "_ignores": [
              "*.not_copy",
              "should_not_be_copy"
            ],
            "name": "awesome_project-prod-1"
          },
          "conf": {
            "updated": "2015-01-01 00:00:00",
            "name": "prod",
            "number": 1
          }
        })

    def test_create(self):
        pass


if __name__ == '__main__':
    unittest.main()
