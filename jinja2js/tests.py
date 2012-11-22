# -*- coding: utf-8 -*-
from extends import inline, function


default_tests = {
	"callable": inline("typeof({{value}}) == 'function'"),
	"number": inline("typeof({{value}}) == 'number'"),
	"string": inline("typeof({{value}}) == 'string'"),

	# todo: ugly, but now it works
	"escaped": function("""function(value) {
        return Jinja.filters.escape(value) == value;
    }""", include="tests", depends='filters.escape'),

	"sequence": function("""function(value) {
        return typeof(value) == 'string' || typeof(value) == 'object';
	}""", include="tests"),

	"mapping": function("""function(value) {
        return value instanceof Object && !(value instanceof Array);
	}""", include="tests"),

	"sameas": inline("{{value}} === {{other}}", spec=('other',)),

	"odd": inline("!!({{value}} % 2)"),
	"even": inline("!({{value}} % 2)"),
	"divisibleby": inline("!({{value}} % {{num}})", spec=('num',)),

	"none": inline("{{value}} === null"),
	"defined": inline("{{value}} !== undefined"),
	"undefined": inline("{{value}} === undefined"),

	"lower": function("""function(value) {
        return value.toLowerCase() == value;
    }""", include="tests"),
	"upper": function("""function(value) {
        return value.toUpperCase() == value;
    }""", include="tests"),
}

default_tests["iterable"] = default_tests["sequence"]
