# -*- coding: utf-8 -*-
import unittest

from jinja2.testsuite import JinjaTestCase
from jinja2 import Markup

from jinja2js.testsuite import Environment

env = Environment()


class FilterTestCase(JinjaTestCase):

    def test_capitalize(self):
        tmpl = env.from_string('{{ "foo bar"|capitalize }}')
        tmpl.assert_render() == 'Foo bar'

    def test_center(self):
        tmpl = env.from_string('{{ "foo"|center(9) }}')
        tmpl.assert_render() == '   foo   '

    def test_default(self):
        tmpl = env.from_string(
            "{{ missing|default('no') }}|{{ false|default('no') }}|"
            "{{ false|default('no', true) }}|{{ given|default('no') }}"
        )
        tmpl.assert_render(given='yes') == 'no|false|no|yes'

    def test_dictsort(self):
        tmpl = env.from_string(
            '{{ foo|dictsort|json }}|'
            '{{ foo|dictsort(true)|json }}|'
            '{{ foo|dictsort(false, "value")|json }}'
        )
        tmpl.assert_render(foo={"aa": 0, "b": 1, "c": 2, "AB": 3}) == '[["aa",0],["AB",3],["b",1],["c",2]]|[["AB",3],["aa",0],["b",1],["c",2]]|[["aa",0],["b",1],["c",2],["AB",3]]'

    def test_batch(self):
        tmpl = env.from_string("{{ foo|batch(3)|json }}|"
                               "{{ foo|batch(3, 'X')|json }}")
        tmpl.assert_render(foo=range(10)) == '[[0,1,2],[3,4,5],[6,7,8],[9]]|[[0,1,2],[3,4,5],[6,7,8],[9,"X","X"]]'

    def test_slice(self):
        tmpl = env.from_string('{{ foo|slice(3)|join("!") }}|'
                               '{{ foo|slice(3, "X")|join("!") }}')
        tmpl.assert_render(foo=range(10)) == "0,1,2,3!4,5,6!7,8,9|0,1,2,3!4,5,6,X!7,8,9,X"

    def test_escape(self):
        tmpl = env.from_string('''{{ '<">&'|escape }}''')
        tmpl.assert_render() == '&lt;&#34;&gt;&amp;'

    def test_striptags(self):
        tmpl = env.from_string('''{{ foo|striptags }}''')
        out = tmpl.assert_render(foo='  <p>just a small   \n <a href="#">'
                          'example</a> link</p>\n<p>to a webpage</p> '
                          '<!-- <p>and some commented stuff</p> -->')
        assert out == 'just a small example link to a webpage'

    def test_filesizeformat(self):
        tmpl = env.from_string(
            '{{ 100|filesizeformat }}|'
            '{{ 1000|filesizeformat }}|'
            '{{ 1000000|filesizeformat }}|'
            '{{ 1000000000|filesizeformat }}|'
            '{{ 1000000000000|filesizeformat }}|'
            '{{ 100|filesizeformat(true) }}|'
            '{{ 1000|filesizeformat(true) }}|'
            '{{ 1000000|filesizeformat(true) }}|'
            '{{ 1000000000|filesizeformat(true) }}|'
            '{{ 1000000000000|filesizeformat(true) }}'
        )
        out = tmpl.assert_render()
        self.assert_equal(out, (
            '100 Bytes|1.0 kB|1.0 MB|1.0 GB|1.0 TB|100 Bytes|'
            '1000 Bytes|976.6 KiB|953.7 MiB|931.3 GiB'
        ))

    def test_filesizeformat_issue59(self):
        tmpl = env.from_string(
            '{{ 300|filesizeformat }}|'
            '{{ 3000|filesizeformat }}|'
            '{{ 3000000|filesizeformat }}|'
            '{{ 3000000000|filesizeformat }}|'
            '{{ 3000000000000|filesizeformat }}|'
            '{{ 300|filesizeformat(true) }}|'
            '{{ 3000|filesizeformat(true) }}|'
            '{{ 3000000|filesizeformat(true) }}'
        )
        out = tmpl.assert_render()
        self.assert_equal(out, (
            '300 Bytes|3.0 kB|3.0 MB|3.0 GB|3.0 TB|300 Bytes|'
            '2.9 KiB|2.9 MiB'
        ))

    def test_first(self):
        tmpl = env.from_string('{{ foo|first }}')
        out = tmpl.assert_render(foo=range(10))
        assert out == '0'

    def test_float(self):
        tmpl = env.from_string('{{ "42"|float }}|'
                               '{{ "ajsghasjgd"|float }}|'
                               '{{ "32.32"|float }}')
        out = tmpl.assert_render()
        assert out == '42|0|32.32'

    def test_format(self):
        tmpl = env.from_string('''{{ "%s|%s"|format("a", "b") }}''')
        out = tmpl.assert_render()
        assert out == 'a|b'

    def test_indent(self):
        tmpl = env.from_string('{{ foo|indent(2) }}|{{ foo|indent(2, true) }}')
        text = '\n'.join([' '.join(['foo', 'bar'] * 2)] * 2)
        out = tmpl.assert_render(foo=text)
        assert out == ('foo bar foo bar\n  foo bar foo bar|  '
                       'foo bar foo bar\n  foo bar foo bar')

    def test_int(self):
        tmpl = env.from_string('{{ "42"|int }}|{{ "ajsghasjgd"|int }}|'
                               '{{ "32.32"|int }}')
        out = tmpl.assert_render()
        assert out == '42|0|32'

    def test_join(self):
        tmpl = env.from_string('{{ [1, 2, 3]|join("|") }}')
        out = tmpl.assert_render()
        assert out == '1|2|3'

        env2 = Environment(autoescape=True)
        tmpl = env2.from_string('{{ ["<foo>", "<span>foo</span>"|safe]|join }}')
        print tmpl.code
        tmpl.assert_render() == '&lt;foo&gt;<span>foo</span>'

    def test_join_attribute(self):
        class User(dict):
            def __init__(self, username):
                self['username'] = username
        tmpl = env.from_string('''{{ users|join(', ', 'username') }}''')
        tmpl.assert_render(users=map(User, ['foo', 'bar'])) == 'foo, bar'

    def test_last(self):
        tmpl = env.from_string('''{{ foo|last }}''')
        out = tmpl.assert_render(foo=range(10))
        assert out == '9'

    def test_length(self):
        tmpl = env.from_string('''{{ "hello world"|length }}''')
        out = tmpl.assert_render()
        assert out == '11'

    def test_lower(self):
        tmpl = env.from_string('''{{ "FOO"|lower }}''')
        out = tmpl.assert_render()
        assert out == 'foo'

    def test_json(self):
        from pprint import pformat
        tmpl = env.from_string('''{{ data|json }}''')
        data = range(3)
        tmpl.assert_render(data=data) == '[0,1,2]'

    def test_random(self):
        tmpl = env.from_string('''{{ seq|random }}''')
        seq = range(100)
        for _ in range(10):
            assert int(tmpl.assert_render(seq=seq)) in seq

    def test_reverse(self):
        tmpl = env.from_string('{{ "foobar"|reverse|join }}|'
                               '{{ [1, 2, 3]|reverse|json }}')
        tmpl.assert_render() == 'raboof|[3,2,1]'

    def test_string(self):
        x = [1, 2, 3, 4, 5]
        tmpl = env.from_string('''{{ obj|string }}''')
        tmpl.assert_render(obj=x) == unicode(x)

    def test_title(self):
        tmpl = env.from_string('''{{ "foo bar"|title }}''')
        tmpl.assert_render() == "Foo Bar"
        tmpl = env.from_string('''{{ "foo's bar"|title }}''')
        tmpl.assert_render() == "Foo's Bar"
        tmpl = env.from_string('''{{ "foo   bar"|title }}''')
        tmpl.assert_render() == "Foo   Bar"
        tmpl = env.from_string('''{{ "f bar f"|title }}''')
        tmpl.assert_render() == "F Bar F"
        tmpl = env.from_string('''{{ "foo-bar"|title }}''')
        tmpl.assert_render() == "Foo-Bar"
        tmpl = env.from_string('''{{ "foo\tbar"|title }}''')
        tmpl.assert_render() == "Foo\tBar"

    def test_truncate(self):
        tmpl = env.from_string(
            '{{ data|truncate(15, true, ">>>") }}|'
            '{{ data|truncate(15, false, ">>>") }}|'
            '{{ smalldata|truncate(15) }}'
        )
        out = tmpl.assert_render(data='foobar baz bar' * 1000,
                          smalldata='foobar baz bar')
        assert out == 'foobar baz barf>>>|foobar baz >>>|foobar baz bar'

    def test_upper(self):
        tmpl = env.from_string('{{ "foo"|upper }}')
        tmpl.assert_render() == 'FOO'

    def test_urlize(self):
        tmpl = env.from_string('{{ "foo http://www.example.com/ bar"|urlize }}')
        tmpl.assert_render() == 'foo <a href="http://www.example.com/">'\
                                'http://www.example.com/</a> bar'

    def test_wordcount(self):
        tmpl = env.from_string('{{ "foo bar baz"|wordcount }}')
        tmpl.assert_render() == '3'

    def test_block(self):
        tmpl = env.from_string('{% filter lower|escape %}<HEHE>{% endfilter %}')
        tmpl.assert_render() == '&lt;hehe&gt;'

    def test_chaining(self):
        tmpl = env.from_string('''{{ ['<foo>', '<bar>']|first|upper|escape }}''')
        tmpl.assert_render() == '&lt;FOO&gt;'

    def test_sum(self):
        tmpl = env.from_string('''{{ [1, 2, 3, 4, 5, 6]|sum }}''')
        tmpl.assert_render() == '21'

    def test_sum_attributes(self):
        tmpl = env.from_string('''{{ values|sum('value') }}''')
        tmpl.assert_render(values=[
            {'value': 23},
            {'value': 1},
            {'value': 18},
        ]) == '42'

    def test_sum_attributes_nested(self):
        tmpl = env.from_string('''{{ values|sum('real.value') }}''')
        tmpl.assert_render(values=[
            {'real': {'value': 23}},
            {'real': {'value': 1}},
            {'real': {'value': 18}},
        ]) == '42'

    def test_abs(self):
        tmpl = env.from_string('''{{ -1|abs }}|{{ 1|abs }}''')
        tmpl.assert_render() == '1|1', tmpl.assert_render()

    def test_round_positive(self):
        tmpl = env.from_string('{{ 2.7|round }}|{{ 2.1|round }}|'
                               "{{ 2.1234|round(3, 'floor') }}|"
                               "{{ 2.1|round(0, 'ceil') }}")
        tmpl.assert_render() == '3|2|2.123|3', tmpl.assert_render()

    def test_round_negative(self):
        tmpl = env.from_string('{{ 21.3|round(-1)}}|'
                               "{{ 21.3|round(-1, 'ceil')}}|"
                               "{{ 21.3|round(-1, 'floor')}}")
        tmpl.assert_render() == '20|30|20', tmpl.assert_render()

    def test_xmlattr(self):
        tmpl = env.from_string("{{ {'foo': 42, 'bar': 23, 'fish': none, "
                               "'spam': missing, 'blub:blub': '<?>'}|xmlattr }}")
        out = tmpl.assert_render().split()
        assert len(out) == 3
        assert 'foo="42"' in out
        assert 'bar="23"' in out
        assert 'blub:blub="&lt;?&gt;"' in out

    def test_sort1(self):
        tmpl = env.from_string('{{ [2, 3, 1]|sort }}|{{ [2, 3, 1]|sort(true) }}')
        tmpl.assert_render() == '1,2,3|3,2,1'

    def test_sort2(self):
        tmpl = env.from_string('{{ (["c", "A", "b", "D"]|sort|join) }}')
        tmpl.assert_render() == 'AbcD'

    def test_sort3(self):
        tmpl = env.from_string('''{{ ['foo', 'Bar', 'blah']|sort }}''')
        tmpl.assert_render() == "Bar,blah,foo"

    def test_sort4(self):
        class Magic(dict):
            def __init__(self, value):
                self['value'] = value

        tmpl = env.from_string('''{{ items|sort(attribute='value')|json }}''')
        tmpl.assert_render(items=map(Magic, [3, 2, 4, 1])) == '[{"value":1},{"value":2},{"value":3},{"value":4}]'

    def test_groupby(self):
        tmpl = env.from_string('''
        {%- for grouper, list in [{'foo': 1, 'bar': 2},
                                  {'foo': 2, 'bar': 3},
                                  {'foo': 1, 'bar': 1},
                                  {'foo': 3, 'bar': 4}]|groupby('foo') -%}
            {{ grouper }}{% for x in list %}: {{ x.foo }}, {{ x.bar }}{% endfor %}|
        {%- endfor %}''')
        tmpl.assert_render().split('|') == [
            "1: 1, 2: 1, 1",
            "2: 2, 3",
            "3: 3, 4",
            ""
        ]

    def test_groupby_tuple_index(self):
        tmpl = env.from_string('''
        {%- for grouper, list in [('a', 1), ('a', 2), ('b', 1)]|groupby(0) -%}
            {{ grouper }}{% for x in list %}:{{ x.1 }}{% endfor %}|
        {%- endfor %}''')
        tmpl.assert_render() == 'a:1:2|b:1|'

    def test_groupby_multidot(self):
        class Date(dict):
            def __init__(self, day, month, year):
                self['day'] = day
                self['month'] = month
                self['year'] = year

        class Article(dict):
            def __init__(self, title, *date):
                self['date'] = Date(*date)
                self['title'] = title

        articles = [
            Article('aha', 1, 1, 1970),
            Article('interesting', 2, 1, 1970),
            Article('really?', 3, 1, 1970),
            Article('totally not', 1, 1, 1971)
        ]
        tmpl = env.from_string('''
        {%- for year, list in articles|groupby('date.year') -%}
            {{ year }}{% for x in list %}[{{ x.title }}]{% endfor %}|
        {%- endfor %}''')
        tmpl.assert_render(articles=articles).split('|') == [
            '1970[aha][interesting][really?]',
            '1971[totally not]',
            ''
        ]

    def test_filtertag(self):
        tmpl = env.from_string("{% filter upper|replace('FOO', 'foo') %}"
                               "foobar{% endfilter %}")
        tmpl.assert_render() == 'fooBAR'

    def test_replace(self):
        env = Environment()
        tmpl = env.from_string('{{ string|replace("o", 42) }}')
        tmpl.assert_render(string='<foo>') == '<f4242>'
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ string|replace("o", 42) }}')
        tmpl.assert_render(string='<foo>') == '&lt;f4242&gt;'
        tmpl = env.from_string('{{ string|replace("<", 42) }}')
        tmpl.assert_render(string='<foo>') == '42foo&gt;'
        tmpl = env.from_string('{{ string|replace("o", ">x<") }}')
        tmpl.assert_render(string=Markup('foo')) == 'f&gt;x&lt;&gt;x&lt;'

    def test_forceescape(self):
        tmpl = env.from_string('{{ x|forceescape }}')
        tmpl.assert_render(x=Markup('<div />')) == u'&lt;div /&gt;'

    def test_safe(self):
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ "<div>foo</div>"|safe }}')
        tmpl.assert_render() == '<div>foo</div>'
        tmpl = env.from_string('{{ "<div>foo</div>" }}')
        tmpl.assert_render() == '&lt;div&gt;foo&lt;/div&gt;'

    def test_urlencode(self):
        env = Environment(autoescape=True)
        tmpl = env.from_string('{{ "Hello, world!"|urlencode }}')
        tmpl.assert_render() == 'Hello%2C%20world%21'
        tmpl = env.from_string('{{ o|urlencode }}')
        tmpl.assert_render(o=u"Hello, world\u203d") == "Hello%2C%20world%E2%80%BD"
        tmpl.assert_render(o=(("f", 1),)) == "f=1"
        tmpl.assert_render(o=(('f', 1), ("z", 2))) == "f=1&amp;z=2"
        tmpl.assert_render(o=((u"\u203d", 1),)) == "%E2%80%BD=1"
        tmpl.assert_render(o={u"\u203d": 1}) == "%E2%80%BD=1"
        tmpl.assert_render(o={0: 1}) == "0=1"


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilterTestCase))
    return suite
