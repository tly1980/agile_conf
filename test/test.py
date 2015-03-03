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


class Prj1Test(unittest.TestCase):
    def setUp(self):

        self.prj_name = 'prj1'
        self.prj_path = os.path.join(
            PROJECT_BASE_PATH, self.prj_name)
        build_path = os.path.join(self.prj_path, '_builds')
        shutil.rmtree(build_path, True)

        self.ret, self.stdout = run_project(
            self.prj_name,
            'agile_conf.py', 'build', '--conf', 'prod.yaml')

    def test_build(self):
        self.assertEqual(self.ret, 0)

        self.assertEqual(
            self.stdout,
            "build started prod/1 ...\nbuild finished\n")

    def test_folder_structure(self):
        flist = list(os.walk(
            os.path.join(self.prj_path, '_builds', 'prod')))
        self.assertEqual(
            flist,
            [
                ('/Users/minddriven/workspace/agile_conf/test/prj1/_builds/prod',
                    ['1'], []),
                ('/Users/minddriven/workspace/agile_conf/test/prj1/_builds/prod/1',
                    ['m1'], []),
                ('/Users/minddriven/workspace/agile_conf/test/prj1/_builds/prod/1/m1',
                    [], ['module.yaml', 'run.sh'])
            ]
        )


if __name__ == '__main__':
    unittest.main()
