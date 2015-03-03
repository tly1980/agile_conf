#!/usr/bin/env python
import subprocess
import os
import unittest
import cStringIO as StringIO
import tempfile
import shutil


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


class Prj1Test(unittest.TestCase):
    def setUp(self):
        self.prj_name = 'prj1'
        self.prj_path = os.path.join(
            PROJECT_BASE_PATH, self.prj_name)

        with open(os.path.join(self.prj_path, 'prod.yaml'), 'wb') as f:
            f.write(DEFAULT_PROD_YAML)

        build_path = os.path.join(self.prj_path, '_builds')
        shutil.rmtree(build_path, True)

    def test_new(self):
        ret, conf_id = run_project(
            self.prj_name,
            'agconf.py', 'id', '--conf', 'prod.yaml')
        self.assertEqual(conf_id.strip(), 'prod/1')

        ret, stdout = run_project(
            self.prj_name,
            'agconf.py', 'new', '--conf', 'prod.yaml')
        self.assertEqual(ret, 0)
        self.assertEqual(
            stdout,
            "Build number +1 to 2 updating file: prod.yaml\n")

        ret, conf_id = run_project(
            self.prj_name,
            'agconf.py', 'id', '--conf', 'prod.yaml')
        self.assertEqual(conf_id.strip(), 'prod/2')

    def test_build(self):
        ret, stdout = run_project(
            self.prj_name,
            'agconf.py', 'build', '--conf', 'prod.yaml')

        self.assertEqual(ret, 0)

        self.assertEqual(
            stdout, "build started prod/1 ...\nbuild finished\n")

    def test_folder_structure(self):
        ret, stdout = run_project(
            self.prj_name,
            'agconf.py', 'build', '--conf', 'prod.yaml')

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
                ['module.yaml', 'run.sh']
            ),

        ]

        self.assertEqual(
            flist_should, flist)


if __name__ == '__main__':
    unittest.main()
