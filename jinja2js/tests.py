# -*- coding: utf-8 -*-
from extends import inline


default_tests = {
	"callable": inline("typeof({{value}}) == 'function'"),
	"number": inline("typeof({{value}}) == 'number'"),
	"string": inline("typeof({{value}}) == 'string'"),

	"odd": inline("!!({{value}} % 2)"),
	"even": inline("!({{value}} % 2)"),
	"divisibleby": inline("!({{value}} % {{num}})", spec=('num',)),

	"none": inline("{{value}} === null"),
	"defined": inline("{{value}} !== undefined"),
	"undefined": inline("{{value}} === undefined"),

	"lower": inline("{{value}}.toLowerCase() == {{value}}"),
	"upper": inline("{{value}}.toUpperCase() == {{value}}"),
}
