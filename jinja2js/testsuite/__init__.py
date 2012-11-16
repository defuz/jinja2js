# -*- coding: utf-8 -*-

from jinja2 import Environment as _Environment


class Template(object):

    def __init__(self, data):
        pass

    def render(self, ctx):
        pass


class Environment(_Environment):

    def from_string(self, data):
        pass

    def get_template(self, data):
        pass


def suite():
    from jinja2.testsuite import \
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
