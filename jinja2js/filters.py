# -*- coding: utf-8 -*-

# todo: different realization for different args count

filters = {
	"safe": "%s",
	"attr": "%s[%s]",
	"length": "%s.length",
	"join": "%s.join(%s)",

	"abs": "Math.abs(%s)",
	"int": "Math.floor(%s) || 0",
	"float": "parseFloat(%s) || 0.0",

	"random": "%(val)s[Math.floor(Math.random() * %(val)s.length)]",

	"string": "%s.toString()",

	"lower": "%s.toLowerCase()",
	"upper": "%s.toUpperCase()",
	"capitalize": "%(val)s.charAt(0).toUpperCase() + %(val)s.substring(1).toLowerCase()",

	"first": "typeof(%(val)s) == 'string' ? %(val)s.charAt(0) : %(val)s[0]",
	"last": "typeof(%(val)s) == 'string' ? %(val)s.charAt(%(val)s.length - 1) : %(val)s[%(val)s.length - 1]",

	"title": "s.replace(/[a-zA-Z]+/g, this.capitalize)",
	"trim": "%s.replace(/^\s+|\s+$/g, '')",
	"wordcount": "%s.split(/\s+/g).length",
	"replace": "%s.replace(%s, %s, 'g')",
	"title": """function(s) {
		return s.replace(/[a-zA-Z]+/g, function(v) {
             return v.charAt(0).toUpperCase() + v.substring(1).toLowerCase();
        });
	}""",

	"escape": """function(s) {
		return (s.replace('&', '&amp;')
		         .replace('<', '&lt;')
		         .replace('>', '&gt;')
		         .replace('"', '&#34;')
		         .replace("'", '&#39;'));
	}""",

	"batch": """function(ls, num, fill) {
		fill = fill === undefined ? null : fill;
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
	}""",

	"center": """function(s, width) {
		width = arguments[1] ? width : 80;
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
	}""",

	"default": """function(val, alt, bool) {
		bool = bool || false;
		if (!bool) {
			return val !== undefined ? val : alt;
		} else {
			return val ? val : alt;
		}
	}""",

	"dictsort": """function(val) {
		var keys = this.list(val);
		keys.sort();
		var ls = [];
		for (var i = 0; i < keys.length; i++) {
			ls.push([keys[i], val[keys[i]]]);
		}
		return ls;
	}""",

	"filesizeformat": """function(val, binary) {
		binary = arguments[1] ? binary : false;
		var bytes = parseFloat(val);
		var base = binary ? 1024 : 1000;
		var middle = binary ? 'i' : '';
		if (bytes < base) {
			var multi = bytes == 1 ? '' : 's';
			return this.format("%i Byte%s", bytes, multi);
		} else if (bytes < base * base) {
			return this.format("%.1f K%sB", bytes / base, middle);
		} else if (bytes < base * base * base) {
			return this.format("%.1f M%sB", bytes / (base * base), middle);
		}
		return this.format("%.1f G%sB", bytes / (base * base * base), middle);
	}""",

	"format": """function(fmt) {
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
	}""",

	"groupby": """function(ls, attr) {
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
	}""",

	"indent": """function(s, w, first) {
		w = w === undefined ? 4 : w;
		first = first === undefined ? false : first;
		var indent = Jasinja.utils.strmul(' ', w);
		var res = s.split('\n').join('\n' + indent);
		if (first) res = indent + res;
		return res;
	}""",

	"list": """function(val) {
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
	}""",

	"reverse": """function(r) {
		var c = r.slice(0);
		c.reverse();
		return c;
	}""",

	"round": """function(val) {
		var num = arguments[1] ? arguments[1] : 0;
		var mul = num ? num * 10 : 1;
		return Math.round(val * mul) / mul;
	}""",

	"slice": """function(ls, num, fill) {
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
	}""",

	"sort": """function(val) {
		var c = val.slice(0);
		c.sort();
		return c;
	}""",

	"sum": """function(ls, attrib, start) {
		start = start === undefined ? 0 : start;
		for (var i = 0; i < ls.length; i++) {
			if (attrib === undefined) start += ls[i];
			else start += ls[i][attrib];
		}
		return start;
	}""",

	"truncate": """function(s, len, kill, end) {

		len = len === undefined ? 255 : len;
		if (s.length < len) return s;
		kill = kill === undefined ? false : kill;
		end = end === undefined ? '...' : end;
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

	}""",

	"xmlattr": """function(d, space) {
		space = space === undefined ? true : space;
		var tmp = [];
		for (var k in d) {
			if (d[k] === null || d[k] === undefined) continue;
			tmp.push(this.format('%s="%s"', this.escape(k), this.escape(d[k])));
		}
		var res = (space ? ' ' : '') + tmp.join(' ');
		return res;
	}"""
}

# synonyms
filters['count'] = filters['length']
filters['e'] = filters['escape']
filters['forceescape'] = filters['escape']
filters['d'] = filters['default']
