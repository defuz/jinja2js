# -*- coding: utf-8 -*-

tests = {
	"callable": "typeof(%s) == 'function'",
	"number": "typeof(%s) == 'number'",
	"string": "typeof(%s) == 'string'"

	"odd": "%s %% 2",
	"even": "!(%s %% 2)",
	"divisibleby": "!(%s %% %s)",

	"none": "%s === null",
	"defined": "%s !== undefined",
	"undefined": "%s === undefined",

	"lower": "%(val)s.toLowerCase() == %(val)s",
	"upper": "%(val)s.toUpperCase() == %(val)s",
}
