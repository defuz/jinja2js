# -*- coding: utf-8 -*-

tests = {
	"callable": """function(val) {
		return typeof(val) == "function";
	}""",
	"defined": """function(val) {
		return val !== undefined;
	}""",
	"divisibleby": """function(val, num) {
		return !(val % num);
	}""",
	"even": """function(val) {
		return this.divisibleby(val, 2);
	}""",
	"lower": """function(val) {
		return val.toLowerCase() == val;
	}""",
	"none": """function(val) {
		return val === null;
	}""",
	"number": """function(val) {
		return typeof(val) == "number";
	}""",
	"odd": """function(val) {
		return !this.divisibleby(val, 2);
	}""",
	"undefined": """function(val) {
		return val === undefined;
	}""",
	"upper": """function(val) {
		return val.toUpperCase() == val;
	}""",
	"string": """function(val) {
		return typeof(val) == "string";
	}"""
}

# tests = {
# 	"callable": "typeof(%s) == 'function'",
# 	"number": "typeof(%s) == 'number'",
# 	"string": "typeof(%s) == 'string'"

# 	"odd": "%s %% 2",
# 	"even": "!(%s %% 2)",
# 	"divisibleby": "!(%s %% %s)",

# 	"none": "%s === null",
# 	"defined": "%s !== undefined",
# 	"undefined": "%s === undefined",

# 	"lower": "%(val)s.toLowerCase() == %(val)s",
# 	"upper": "%(val)s.toUpperCase() == %(val)s",
# }
