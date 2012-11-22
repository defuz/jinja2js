# -*- coding: utf-8 -*-
from extends import function, inline

# todo: light autoescaping: |safe can be use only in the end of output


# todo: check `.toString()` in all filters/test
# todo: check `is string` in all filters/test result
# todo: default arguments: null -> undefined


default_filters = {
	"safe": inline("{{value}}"),
	"attr": inline("{{value}}[{{name}}]", spec='name'),
	"length": inline("{{value}}.length"),

	"abs": inline("Math.abs({{value}})"),
	"int": inline("Math.floor({{value}}) || {{default}}", spec="default", defaults={'default': 0}),
	"float": inline("parseFloat({{value}}) || {{default}}", spec="default", defaults={'default': 0.0}),

	"string": inline("{{value}}.toString()"),

	"lower": inline("{{value}}.toLowerCase()"),
	"upper": inline("{{value}}.toUpperCase()"),

	"trim": inline("{{value}}.replace(/^\s+|\s+$/g, '')"),
	"wordcount": inline("{{value}}.split(/\s+/g).length"),
	"replace": inline("{{value}}.split({{old}}).join({{new}})", spec=('old', 'new')),

	"urlencode": function("""function(value) {
        if (value instanceof Array) {
        	var r = [];
        	for (var i in value) {
        		r.push(encodeURIComponent(value[i][0]) + "=" + encodeURIComponent(value[i][1]));
        	}
        	return r.join('&amp;');
        }
        if (typeof value == "object") {
        	var r = [];
        	for (var i in value) {
        		r.push(encodeURIComponent(i) + "=" + encodeURIComponent(value[i]));
        	}
        	return r.join('&amp;');
        }
        return encodeURIComponent(value);
    }"""),

	"json": inline('JSON.stringify({{value}})'),

	"join": function("""function(arr, del, attr) {
        if (!(arr instanceof Array)) {
        	if (attr) {
        		return arr[attr];
        	}
        	return arr;
        }
        if (attr) {
            r = [];
            for (var i in arr) {
            	r.push(arr[i][attr])
            }
            return r.join(del);
        }
        return arr.join(del);
    }""", spec=('d', 'attribute'), defaults={'d': '', 'attribute': None}),

	"title": function("""function(value) {
      	return value.replace(/[a-zA-Z]+/g, function(v) {
             return v.charAt(0).toUpperCase() + v.substring(1).toLowerCase();
        });
  	}"""),

	"capitalize": function("""function(value) {
        return value.charAt(0).toUpperCase() + value.substring(1).toLowerCase();
    }"""),

	"first": function("""function(value) {
        return typeof(value) == 'string' ? value.charAt(0) : value[0];
    }"""),

	"last": function("""function(value) {
        return typeof(value) == 'string' ? value.charAt(value.length - 1) : value[value.length - 1];
    }"""),

	"random": function("""function(value) {
        return value[Math.floor(Math.random() * value.length)];
    }"""),

	"escape": function("""function(s) {
		return s.toString().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&#34;').replace("'", '&#39;');
	}"""),

	"striptags": function("""function(s) {
        return s.toString().replace(/(<!--.*?-->|<[^>]*>)/g, ' ').replace(/\\s+/g, ' ').trim();
    }"""),

    "urlize": function("""function(s) {
        return s.toString().replace(/(\\b(https?|ftp|file):\\/\\/[-A-Z0-9+&@#\\/%?=~_|!:,.;]*[-A-Z0-9+&@#\\/%=~_|])/ig, '<a href="$1">$1</a>');
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
	}""", spec=('linecount', 'fill_with')),

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
	}""", spec='width', defaults={'width': 80}),

	"default": function("""function(val, alt, bool) {
		if (!bool) {
			return val !== undefined ? val : alt;
		} else {
			return val ? val : alt;
		}
	}""", spec=('default_value', 'boolean'), defaults={'default_value': '', 'boolean': False}),

	"dictsort": function("""function(val, case_sensitive, by) {
        var items = [], ls = [], i, key;
        for (i in val) {
        	key = (by == 'key' ? i : val[i]).toString();
        	if (!case_sensitive) {
        		key = key.toLowerCase();
        	}
    		items.push([key, i, val[i]]);
        }
		items.sort();
		for (i = 0; i < items.length; i++) {
			ls.push([items[i][1], items[i][2]]);
		}
		return ls;
	}""", spec=('case_sensitive', 'by'), defaults={'case_sensitive': False, 'by': 'key'}),

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
	}""", spec='binary', defaults={'binary': False}, depends='filters.format'),

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
					val = Jinja.utils.strmul(ext, wantlen - val.length) + val;
				}
				fmt = fmt.replace(parts[0], val);
			} else if (type == "i") {
				val = parseInt(val).toString();
				if (val.length < wantlen) {
					val = Jinja.utils.strmul(ext, wantlen - val.length) + val;
				}
				fmt = fmt.replace(parts[0], val);
			} else if (type == "s") {
				if (val.length < wantlen) {
					val = Jinja.utils.strmul(ext, wantlen - val.length) + val;
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
		var indent = Jinja.utils.strmul(' ', w);
		var res = s.split('\\n').join('\\n' + indent);
		if (first) res = indent + res;
		return res;
	}""", spec=('width', 'indentfirst'), defaults={'width': 4, 'indentfirst': False}, depends='utils.strmul'),

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

	"sort": function("""function(arr, reverse, caseSens, attr) {
        arr.sort(function(a, b) {
            var x, y;

            if(attr) {
                x = a[attr];
                y = b[attr];
            }
            else {
                x = a;
                y = b;
            }

            if(!caseSens && typeof(x) == 'string' && typeof(y) == 'string') {
                x = x.toLowerCase();
                y = y.toLowerCase();
            }

            if(x < y) {
                return reverse ? 1 : -1;
            }
            else if(x > y) {
                return reverse ? -1: 1;
            }
            else {
                return 0;
            }
        });

        return arr;
    }""", spec=('reverse', 'case_sensitive', 'attribute'), defaults={'reverse': False, 'case_sensitive': False, 'attribute': None}),

	"sum": function("""function(ls, attrib, start) {
        if (attrib !== undefined) {
        	attrib = attrib.split('.')
        }
		for (var i = 0; i < ls.length; i++) {
			if (attrib === undefined) {
				start += ls[i];
			} else {
				var x = ls[i];
				for (var j in attrib) {
					x = x[attrib[j]];
				}
				start += x;
			}
		}
		return start;
	}""", spec=('attribute', 'start'), defaults={'start': 0}),

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

	}""", spec=('length', 'killwords', 'end'), defaults={'length': 255, 'killwords': False, 'end': '...'}),

	"xmlattr": function("""function(d, space) {
		var tmp = [];
		for (var k in d) {
			if (d[k] === null || d[k] === undefined) continue;
			tmp.push(Jinja.filters.format('%s="%s"', Jinja.filters.escape(k), Jinja.filters.escape(d[k])));
		}
		var res = (space ? ' ' : '') + tmp.join(' ');
		return res;
	}""", spec='autospace', defaults={'autospace': True}, depends=('filters.escape', 'filters.format'))
}

# synonyms
default_filters['count'] = default_filters['length']
default_filters['forceescape'] = default_filters['e'] = default_filters['escape']
default_filters['d'] = default_filters['default']

# i do not want to imitate `pprint`. so this is an acceptable alternative
default_filters['pprint'] = default_filters['json']
