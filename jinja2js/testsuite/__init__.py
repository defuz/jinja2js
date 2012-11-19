# -*- coding: utf-8 -*-
import sys
from os import path
from tempfile import mkstemp
from subprocess import Popen, PIPE
from json import dumps

from jinja2 import Environment as _Environment
from jinja2js import Jinja2JS

# add "jinja2js" directory to sys.path
sys.path.append(path.dirname(path.dirname(__file__)))


class JSTemplateRuntimeError(Exception):
    pass


class Template(object):

    NODE_SUFFIX = """
process.stdin.resume();
process.stdin.setEncoding('utf8');
process.stdin.on('data', function (data) {
    process.stdout.write(Jinja.templates[process.argv[2]]
                         .render(JSON.parse(data)));
    process.exit();
});"""

    def __new__(cls, source=None, name='<template>', code=None):
        if source:
            return Environment().from_string(source)
        return super(object, cls).__new__(name, code)

    def __init__(self, name, code):
        self.name = name
        self.file = mkstemp()
        self.file.write(code)
        self.file.write(NODE_SUFFIX)
        self.file.close()

    def render(self, ctx):
        p = Popen(['node', self.file.name, self.name],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(dumps(ctx))
        if stderr:
            raise JSTemplateRuntimeError(stderr)
        return stdout


class Environment(_Environment):

    def __init__(self):
        super(_Environment, self).__init__(extentions=[Jinja2JS])

    def from_string(self, source):
        return Template(code=self.compile_js(source=source))

    def get_template(self, name):
        return Template(name=name, code=self.compile_js(templates=[name]))


def suite():
    from jinja2js.testsuite import \
        core_tags, imports, inheritance, regression, security, filters, tests

    suite = unittest.TestSuite()
    suite.addTest(filters.suite())
    suite.addTest(tests.suite())
    suite.addTest(core_tags.suite())
    suite.addTest(inheritance.suite())
    suite.addTest(imports.suite())
    suite.addTest(security.suite())
    suite.addTest(regression.suite())

    return suite
