# -*- coding: utf-8 -*-
import unittest

from jinja2.testsuite import JinjaTestCase
from jinja2 import Markup

from jinja2js.testsuite import Environment

env = Environment()


class TestsTestCase(JinjaTestCase):

    def test_defined(self):
        tmpl = env.from_string('{{ missing is defined }}|{{ true is defined }}')
        tmpl.assert_render() == 'false|true'

    def test_even(self):
        tmpl = env.from_string('''{{ 1 is even }}|{{ 2 is even }}''')
        tmpl.assert_render() == 'false|true'

    def test_odd(self):
        tmpl = env.from_string('''{{ 1 is odd }}|{{ 2 is odd }}''')
        tmpl.assert_render() == 'true|false'

    def test_lower(self):
        tmpl = env.from_string('''{{ "foo" is lower }}|{{ "FOO" is lower }}''')
        tmpl.assert_render() == 'true|false'

    def test_typechecks(self):
        tmpl = env.from_string('''
            {{ 42 is undefined }}
            {{ 42 is defined }}
            {{ 42 is undefined }}
            {{ undefined is undefined }}
            {{ 42 is number }}
            {{ 42 is string }}
            {{ "foo" is string }}
            {{ "foo" is sequence }}
            {{ [1] is sequence }}
            {{ range is callable }}
            {{ 42 is callable }}
            {{ [1,2,3,4,5] is iterable }}
            {{ {} is mapping }}
            {{ mydict is mapping }}
            {{ [] is mapping }}
        ''')

        class MyDict(dict):
            pass
        tmpl.assert_render(mydict=MyDict()).split() == [
            'false', 'true', 'false', 'true', 'true', 'false',
            'true', 'true', 'true', 'true', 'false', 'true',
            'true', 'true', 'false'
        ]

    def test_sequence(self):
        tmpl = env.from_string(
            '{{ [1, 2, 3] is sequence }}|'
            '{{ "foo" is sequence }}|'
            '{{ 42 is sequence }}'
        )
        tmpl.assert_render() == 'true|true|false'

    def test_upper(self):
        tmpl = env.from_string('{{ "FOO" is upper }}|{{ "foo" is upper }}')
        tmpl.assert_render() == 'true|false'

    def test_sameas(self):
        tmpl = env.from_string('{{ foo is sameas false }}|'
                               '{{ 0 is sameas false }}')
        tmpl.assert_render(foo=False) == 'true|false'

    def test_no_paren_for_arg1(self):
        tmpl = env.from_string('{{ foo is sameas null }}')
        tmpl.assert_render(foo=None) == 'true'

    def test_escaped(self):
        env = Environment(autoescape='false')
        tmpl = env.from_string('{{ x is escaped }}|{{ y is escaped }}')
        tmpl.assert_render(x='foo', y=Markup('foo')) == 'false|true'


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestsTestCase))
    return suite
