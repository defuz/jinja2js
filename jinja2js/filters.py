# -*- coding: utf-8 -*-
from extends import function, inline


default_filters = {
	"safe": inline("{{value}}"),
	"attr": inline("{{value}}[{{name}}]", spec='name'),
	"length": inline("{{value}}.length"),
	"join": inline("{{value}}.join({{d}})", spec='d'),

	"abs": inline("Math.abs({{value}})"),
	"int": inline("Math.floor({{value}}) || {{default}}", spec="default", default={'default': 0}),
	"float": inline("parseFloat({{value}}) || {{default}}", spec="default", default={'default': 0}),

	"random": inline("{{value}}[Math.floor(Math.random() * {{value}}.length)]"),

	"string": inline("{{value}}.toString()"),

	"lower": inline("{{value}}.toLowerCase()"),
	"upper": inline("{{value}}.toUpperCase()"),
	"capitalize": inline("{{value}}.charAt(0).toUpperCase() + {{value}}.substring(1).toLowerCase()"),

	"first": inline("typeof({{value}} == 'string' ? {{value}}.charAt(0) : {{value}}[0]"),
	"last": inline("typeof({{value}}) == 'string' ? {{value}}.charAt({{value}}.length - 1) : {{value}}[{{value}}.length - 1]"),

	"trim": inline("{{value}}.replace(/^\s+|\s+$/g, '')"),
	"wordcount": inline("{{value}}.split(/\s+/g).length"),
	"replace": inline("{{value}}.replace({{old}}, {{new}}, 'g')", spec=('old', 'new')),


	"title": function("""function(value) {
      	return value.replace(/[a-zA-Z]+/g, function(v) {
             return v.charAt(0).toUpperCase() + v.substring(1).toLowerCase();
        });
  	}"""),

	"escape": function("""function(s) {
		return (s.replace('&', '&amp;')
		         .replace('<', '&lt;')
		         .replace('>', '&gt;')
		         .replace('"', '&#34;')
		         .replace("'", '&#39;'));
	}"""),

	"batch": function("""function(ls, num, fill) {
		var res = [];
		var tmp = [];
		for (var i = 0; i < ls.length; i++) {
			if (tmp.length == num) {
				res.push(tmp);
				tmp = [];
			}
			tmp.push(ls[i]);
		}
		if (tmp.length && tmp.length < num && fill) {
			for (var i = num - 1; i > 0; i--) {
				tmp.push(fill);
			}
		}
		if (tmp.length) res.push(tmp);
		return res;
	}""", spec=('linecount', 'fill_with'), default={'fill_with': None}),

	"center": function("""function(s, width) {
		var pre = Math.floor((width - s.length) / 2);
		var post = Math.ceil((width - s.length) / 2);
		var buf = [];
		for (var i = 0; i < pre; i++) {
			buf.push(' ');
		}
		buf.push(s);
		for (var i = 0; i < post; i++) {
			buf.push(' ');
		}
		return buf.join('');
	}""", spec='width', default={'width': 80}),

	"default": function("""function(val, alt, bool) {
		if (!bool) {
			return val !== undefined ? val : alt;
		} else {
			return val ? val : alt;
		}
	}""", spec=('default_value', 'boolean'), default={'default_value': '', 'boolean': False}),

	"dictsort": function("""function(val) {
		var keys = Jinja.filters.list(val);
		keys.sort();
		var ls = [];
		for (var i = 0; i < keys.length; i++) {
			ls.push([keys[i], val[keys[i]]]);
		}
		return ls;
	}""", depends='filters.list'),

	"filesizeformat": function("""function(val, binary) {
		var bytes = parseFloat(val);
		var base = binary ? 1024 : 1000;
		var middle = binary ? 'i' : '';
		if (bytes < base) {
			var multi = bytes == 1 ? '' : 's';
			return Jinja.filters.format("%i Byte%s", bytes, multi);
		} else if (bytes < base * base) {
			return Jinja.filters.format("%.1f K%sB", bytes / base, middle);
		} else if (bytes < base * base * base) {
			return Jinja.filters.format("%.1f M%sB", bytes / (base * base), middle);
		}
		return Jinja.filters.format("%.1f G%sB", bytes / (base * base * base), middle);
	}""", spec='binary', default={'binary': False}, depends='filter.format'),

	"format": function("""function(fmt) {
		var vals = Array.prototype.slice.call(arguments, 1);
		var regex = new RegExp('\%([0 ]?)((?:[0-9]+)?)(\.[0-9]+)?([fis%])');
		while (regex.test(fmt)) {
			var parts = regex.exec(fmt);
			var ext = parts[1] ? parts[1] : ' ';
			var wantlen = parseInt(parts[2]);
			var type = parts[0].substring(parts[0].length - 1);
			var val = vals.shift();
			if (type == "f") {
				val = parseFloat(val);
				if (parts[3]) {
					val = val.toFixed(parseInt(parts[3].substring(1)));
				} else {
					val = val.toString();
				}
				if (val.length < wantlen) {
					val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
				}
				fmt = fmt.replace(parts[0], val);
			} else if (type == "i") {
				val = parseInt(val).toString();
				if (val.length < wantlen) {
					val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
				}
				fmt = fmt.replace(parts[0], val);
			} else if (type == "s") {
				if (val.length < wantlen) {
					val = Jasinja.utils.strmul(ext, wantlen - val.length) + val;
				}
				fmt = fmt.replace(parts[0], val.toString());
			} else if (type == "%") {
				fmt = fmt.replace("%%", "%");
			}
		}
		return fmt;
	}""", free=True, depends='utils.strmul'),

	"groupby": function("""function(ls, attr) {
		var groups = {};
		for (var i = 0; i < ls.length; i++) {
			var key = ls[i][attr];
			if (!(key in groups)) groups[key] = [];
			groups[key].push(ls[i]);
		}
		var res = [];
		for (var key in groups) {
			res.push({0: key, grouper: key, 1: groups[key], list: groups[key]});
		}
		return res;
	}""", spec='attribute'),

	"indent": function("""function(s, w, first) {
		var indent = Jasinja.utils.strmul(' ', w);
		var res = s.split('\n').join('\n' + indent);
		if (first) res = indent + res;
		return res;
	}""", spec=('width', 'indentfirst'), default={'width': 4, 'indentfirst': False}, depends='utils.strmul'),

	"list": function("""function(val) {
		if (val instanceof Array) {
			return val;
		} else if (typeof(val) == "string") {
			var ls = [];
			for (var i = 0; i < val.length; i++) {
				ls.push(val.charAt(i));
			}
			return ls;
		} else if (typeof(val) == "object") {
			var ls = [];
			for (var key in val) {
				ls.push(key);
			}
			return ls;
		} else {
			throw new TypeError("containment is undefined");
		}
	}"""),

	"reverse": function("""function(r) {
		var c = r.slice(0);
		c.reverse();
		return c;
	}"""),

	"round": function("""function(val) {
		var num = arguments[1] ? arguments[1] : 0;
		var mul = num ? num * 10 : 1;
		return Math.round(val * mul) / mul;
	}"""),

	"slice": function("""function(ls, num, fill) {
		var ssize = Math.floor(ls.length / num);
		var extra = ls.length % num;
		var offset = 0;
		var res = [];
		var offset = 0;
		for (var i = 0; i < num; i++) {
			var start = offset + i * ssize;
			if (i < extra) offset += 1;
			var end = offset + (i + 1) * ssize;
			var tmp = ls.slice(start, end);
			if (fill !== undefined && i >= extra) {
				tmp.push(fill);
			}
			res.push(tmp);
		}
		return res;
	}""", spec=('slices', 'fill_with')),

	"sort": function("""function(val) {
		var c = val.slice(0);
		c.sort();
		return c;
	}"""),

	"sum": function("""function(ls, attrib, start) {
		for (var i = 0; i < ls.length; i++) {
			if (attrib === undefined) start += ls[i];
			else start += ls[i][attrib];
		}
		return start;
	}""", spec=('attribute', 'start'), default={'attribute': None, 'start': 0}),

	"truncate": function("""function(s, len, kill, end) {
		if (s.length < len) return s;
		if (kill) return s.substring(0, len) + end;

		var words = s.split(' ');
		var result = [];
		var m = 0;
		for (var i = 0; i < words.length; i++) {
			m += words[i].length + 1
			if (m > len) break;
			result.push(words[i]);
		}
		result.push(end);
		return result.join(' ');

	}""", spec=('length', 'killwords', 'end'), default={'length': 255, 'killwords': False, 'end': '...'}),

	"xmlattr": function("""function(d, space) {
		var tmp = [];
		for (var k in d) {
			if (d[k] === null || d[k] === undefined) continue;
			tmp.push(Jinja.filters.format('%s="%s"', Jinja.filters.escape(k), Jinja.filters.escape(d[k])));
		}
		var res = (space ? ' ' : '') + tmp.join(' ');
		return res;
	}""", spec='autospace', default={'autospace': True}, depends='filters.escape')
}

# synonyms
default_filters['count'] = default_filters['length']
default_filters['e'] = default_filters['escape']
default_filters['forceescape'] = default_filters['escape']
default_filters['d'] = default_filters['default']
