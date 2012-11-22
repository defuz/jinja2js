# -*- coding: utf-8 -*-
import unittest
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE, STDOUT
from json import dumps

from jinja2 import Environment as _Environment
from jinja2js import Jinja2JS


# todo: test others test suite
# todo: restore all test suite from origin jinja rep


class JSTemplateRuntimeError(Exception):
    pass


class AssertString(str):

    def __eq__(self, other):
        equal = str.__eq__(self, other)
        if equal is False:
            raise AssertionError("%r != %r" % (self, other))
        return equal


class Template(object):

    NODE_SUFFIX = """
process.stdin.resume();
process.stdin.setEncoding('utf8');
process.stdin.on('data', function (data) {
    process.stdout.write(Jinja.templates[process.argv[2]]
                         .render(JSON.parse(data)));
    process.exit();
});"""

    def __init__(self, source=None, name='<template>', code=None):
        if source:
            code = Environment().compile_js(source=source)
        self.name = name
        self.code = code
        self.file = NamedTemporaryFile(suffix='.js')
        self.file.write(code)
        self.file.write(Template.NODE_SUFFIX)
        self.file.flush()

    def render(self, ctx=None, **ctx2):
        ctx = ctx or ctx2
        p = Popen(['node', self.file.name, self.name],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(dumps(ctx))
        if stderr:
            raise JSTemplateRuntimeError(stderr)
        return stdout

    def assert_render(self, *args, **kwargs):
        return AssertString(self.render(*args, **kwargs))


class Environment(_Environment):

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self.add_extension(Jinja2JS)

    def from_string(self, source):
        return Template(code=self.compile_js(source=source))

    def get_template(self, name):
        return Template(name=name, code=self.compile_js(templates=[name]))


def suite():
    from jinja2js.testsuite import \
        core_tags, imports, inheritance, regression, security, filters, tests

    suite = unittest.TestSuite()
    suite.addTest(filters.suite())
    # suite.addTest(tests.suite())
    # suite.addTest(core_tags.suite())
    # suite.addTest(inheritance.suite())
    # suite.addTest(imports.suite())
    # suite.addTest(security.suite())
    # suite.addTest(regression.suite())

    return suite
