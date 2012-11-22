# -*- coding: utf-8 -*-
import unittest

from jinja2.testsuite import JinjaTestCase
from jinja2 import DictLoader

from jinja2js.testsuite import Environment, JSTemplateRuntimeError

env = Environment()


class ForLoopTestCase(JinjaTestCase):

    def test_simple(self):
        tmpl = env.from_string('{% for item in seq %}{{ item }}{% endfor %}')
        tmpl.assert_render(seq=range(10)) == '0123456789'

    def test_else(self):
        tmpl = env.from_string('{% for item in seq %}XXX{% else %}...{% endfor %}')
        tmpl.assert_render() == '...'

    def test_empty_blocks(self):
        tmpl = env.from_string('<{% for item in seq %}{% else %}{% endfor %}>')
        tmpl.assert_render() == '<>'

    def test_context_vars(self):
        tmpl = env.from_string('''{% for item in seq -%}
        {{ loop.index }}|{{ loop.index0 }}|{{ loop.revindex }}|{{
            loop.revindex0 }}|{{ loop.first }}|{{ loop.last }}|{{
           loop.length }}###{% endfor %}''')
        one, two, _ = tmpl.assert_render(seq=[0, 1]).split('###')
        (one_index, one_index0, one_revindex, one_revindex0, one_first,
         one_last, one_length) = one.split('|')
        (two_index, two_index0, two_revindex, two_revindex0, two_first,
         two_last, two_length) = two.split('|')

        assert int(one_index) == 1 and int(two_index) == 2
        assert int(one_index0) == 0 and int(two_index0) == 1
        assert int(one_revindex) == 2 and int(two_revindex) == 1
        assert int(one_revindex0) == 1 and int(two_revindex0) == 0
        assert one_first == 'true' and two_first == 'false'
        assert one_last == 'false' and two_last == 'true'
        assert one_length == two_length == '2'

    def test_cycling(self):
        tmpl = env.from_string('''{% for item in seq %}{{
            loop.cycle('<1>', '<2>') }}{% endfor %}''')
        output = tmpl.assert_render(seq=range(4))
        assert output == '<1><2>' * 2

    def test_scope(self):
        tmpl = env.from_string('{% for item in seq %}{% endfor %}{{ item }}')
        output = tmpl.assert_render(seq=range(10))
        assert not output

    def test_noniter(self):
        tmpl = env.from_string('{% for item in none %}...{% endfor %}')
        self.assert_raises(JSTemplateRuntimeError, tmpl.render)

    def test_recursive(self):
        tmpl = env.from_string('''{% for item in seq recursive -%}
            [{{ item.a }}{% if item.b %}<{{ loop(item.b) }}>{% endif %}]
        {%- endfor %}''')
        tmpl.assert_render(seq=[
            dict(a=1, b=[dict(a=1), dict(a=2)]),
            dict(a=2, b=[dict(a=1), dict(a=2)]),
            dict(a=3, b=[dict(a='a')])
        ]) == '[1<[1][2]>][2<[1][2]>][3<[a]>]'

    def test_looploop(self):
        tmpl = env.from_string('''{% for row in table %}
            {%- set rowloop = loop -%}
            {% for cell in row -%}
                [{{ rowloop.index }}|{{ loop.index }}]
            {%- endfor %}
        {%- endfor %}''')
        tmpl.assert_render(table=['ab', 'cd']) == '[1|1][1|2][2|1][2|2]'

    def test_loop_errors(self):
        tmpl = env.from_string('''{% for item in [1] if loop.index
                                      == 0 %}...{% endfor %}''')
        self.assert_raises(JSTemplateRuntimeError, tmpl.render)
        tmpl = env.from_string('''{% for item in [] %}...{% else
            %}{{ loop }}{% endfor %}''')
        tmpl.assert_render() == ''

    def test_loop_filter(self):
        tmpl = env.from_string('{% for item in [0,1,2,3,4,5,6,7,8,9] if item '
                               'is even %}[{{ item }}]{% endfor %}')
        tmpl.assert_render() == '[0][2][4][6][8]'
        tmpl = env.from_string('''
            {%- for item in [0,1,2,3,4,5,6,7,8,9] if item is even %}[{{
                loop.index }}:{{ item }}]{% endfor %}''')
        tmpl.assert_render() == '[1:0][2:2][3:4][4:6][5:8]'

    def test_loop_unassignable(self):
        self.assert_raises(JSTemplateRuntimeError, env.from_string,
                           '{% for loop in seq %}...{% endfor %}')

    def test_scoped_special_var(self):
        t = env.from_string('{% for s in seq %}[{{ loop.first }}{% for c in s %}'
                            '|{{ loop.first }}{% endfor %}]{% endfor %}')
        t.assert_render(seq=('ab', 'cd')) == '[true|true|false][false|true|false]'

    def test_scoped_loop_var(self):
        t = env.from_string('{% for x in seq %}{{ loop.first }}'
                            '{% for y in seq %}{% endfor %}{% endfor %}')
        t.assert_render(seq='ab') == 'truefalse'
        t = env.from_string('{% for x in seq %}{% for y in seq %}'
                            '{{ loop.first }}{% endfor %}{% endfor %}')
        t.assert_render(seq='ab') == 'truefalsetruefalse'

    def test_recursive_empty_loop_iter(self):
        t = env.from_string('''
        {%- for item in foo recursive -%}{%- endfor -%}
        ''')
        t.assert_render(dict(foo=[])) == ''

    def test_call_in_loop(self):
        t = env.from_string('''
        {%- macro do_something() -%}
            [{{ caller() }}]
        {%- endmacro %}

        {%- for i in [1, 2, 3] %}
            {%- call do_something() -%}
                {{ i }}
            {%- endcall %}
        {%- endfor -%}
        ''')
        t.assert_render() == '[1][2][3]'

    def test_scoping_bug(self):
        t = env.from_string('''
        {%- for item in foo %}...{{ item }}...{% endfor %}
        {%- macro item(a) %}...{{ a }}...{% endmacro %}
        {{- item(2) -}}
        ''')
        t.assert_render(foo=(1,)) == '...1......2...'

    def test_unpacking(self):
        tmpl = env.from_string('{% for a, b, c in [[1, 2, 3]] %}'
            '{{ a }}|{{ b }}|{{ c }}{% endfor %}')
        tmpl.assert_render() == '1|2|3'


class IfConditionTestCase(JinjaTestCase):

    def test_simple(self):
        tmpl = env.from_string('''{% if true %}...{% endif %}''')
        tmpl.assert_render() == '...'

    def test_elif(self):
        tmpl = env.from_string('''{% if false %}XXX{% elif true
            %}...{% else %}XXX{% endif %}''')
        tmpl.assert_render() == '...'

    def test_else(self):
        tmpl = env.from_string('{% if false %}XXX{% else %}...{% endif %}')
        tmpl.assert_render() == '...'

    def test_empty(self):
        tmpl = env.from_string('[{% if true %}{% else %}{% endif %}]')
        tmpl.assert_render() == '[]'

    def test_complete(self):
        tmpl = env.from_string('{% if a %}A{% elif b %}B{% elif c == d %}'
                               'C{% else %}D{% endif %}')
        tmpl.assert_render(a=0, b=False, c=42, d=42.0) == 'C'

    def test_no_scope(self):
        tmpl = env.from_string('{% if a %}{% set foo = 1 %}{% endif %}{{ foo }}')
        tmpl.assert_render(a=True) == '1'
        tmpl = env.from_string('{% if true %}{% set foo = 1 %}{% endif %}{{ foo }}')
        tmpl.assert_render() == '1'


class MacrosTestCase(JinjaTestCase):
    env = Environment(trim_blocks=True)

    def test_simple(self):
        tmpl = self.env.from_string('''\
{% macro say_hello(name) %}Hello {{ name }}!{% endmacro %}
{{ say_hello('Peter') }}''')
        tmpl.assert_render() == 'Hello Peter!'

    def test_scoping(self):
        tmpl = self.env.from_string('''\
{% macro level1(data1) %}
{% macro level2(data2) %}{{ data1 }}|{{ data2 }}{% endmacro %}
{{ level2('bar') }}{% endmacro %}
{{ level1('foo') }}''')
        tmpl.assert_render() == 'foo|bar'

    def test_arguments(self):
        tmpl = self.env.from_string('''\
{% macro m(a, b, c='c', d='d') %}{{ a }}|{{ b }}|{{ c }}|{{ d }}{% endmacro %}
{{ m() }}|{{ m('a') }}|{{ m('a', 'b') }}|{{ m(1, 2, 3) }}''')
        tmpl.assert_render() == '||c|d|a||c|d|a|b|c|d|1|2|3|d'

    def test_varargs(self):
        tmpl = self.env.from_string('''\
{% macro test() %}{{ varargs|join('|') }}{% endmacro %}\
{{ test(1, 2, 3) }}''')
        tmpl.assert_render() == '1|2|3'

    def test_simple_call(self):
        tmpl = self.env.from_string('''\
{% macro test() %}[[{{ caller() }}]]{% endmacro %}\
{% call test() %}data{% endcall %}''')
        tmpl.assert_render() == '[[data]]'

    def test_complex_call(self):
        tmpl = self.env.from_string('''\
{% macro test() %}[[{{ caller('data') }}]]{% endmacro %}\
{% call(data) test() %}{{ data }}{% endcall %}''')
        tmpl.assert_render() == '[[data]]'

    def test_caller_undefined(self):
        tmpl = self.env.from_string('''\
{% set caller = 42 %}\
{% macro test() %}{{ caller is not defined }}{% endmacro %}\
{{ test() }}''')
        tmpl.assert_render() == 'true'

    def test_include(self):
        self.env = Environment(loader=DictLoader({'include':
            '{% macro test(foo) %}[{{ foo }}]{% endmacro %}'}))
        tmpl = self.env.from_string('{% from "include" import test %}{{ test("foo") }}')
        tmpl.assert_render() == '[foo]'

    def test_callself(self):
        tmpl = self.env.from_string('{% macro foo(x) %}{{ x }}{% if x > 1 %}|'
                                    '{{ foo(x - 1) }}{% endif %}{% endmacro %}'
                                    '{{ foo(5) }}')
        tmpl.assert_render() == '5|4|3|2|1'


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ForLoopTestCase))
    suite.addTest(unittest.makeSuite(IfConditionTestCase))
    suite.addTest(unittest.makeSuite(MacrosTestCase))
    return suite
