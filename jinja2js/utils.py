# -*- coding: utf-8 -*-
from extends import function

# todo: add global functions
# http://jinja.pocoo.org/docs/templates/#list-of-global-functions
# using "None" in templates

default_utils = {
	"markup": function("""(function() {
        var Markup = function(html) {
        	this.html = html;
        }
        Markup.prototype.toString = function() {
        	return this.html;
        }
        return Markup;
   	})()""", include='utils'),

	"extend": function("""function(base, child) {
		if (child == undefined) return base;
		var current = {"blocks": {}};
		for (var key in base.blocks) {
			if (!child.blocks[key]) {
				current.blocks[key] = base.blocks[key];
			} else {
				current.blocks[key] = child.blocks[key];
			}
		}
		return current;
	}""", include='utils'),

	"slice": function("""function(val, start, stop) {
		if (typeof(val) == "string") {
			return val.substring(start, stop);
		} else if (val instanceof Array) {
			return val.slice(start, stop);
		}
	}""", include='utils'),

	"loop": function("""function(iter) {
		function LoopObject() {
			this.iter = iter;
			this.l = iter.length;
			this.i = 0;
			this.update = function() {
				if (arguments.length) this.i = arguments[0];
				this.index = this.i + 1;
				this.index0 = this.i;
				this.revindex = this.l - this.i;
				this.revindex0 = this.l - this.i - 1;
				this.first = !this.i;
				this.last = this.i == this.l - 1;
			}
			this.cycle = function() {
				return arguments[this.index0 % arguments.length];
			};
		}
		return new LoopObject();
	}""", include='utils'),

	"contains": function("""function(n, hs) {
		if (hs instanceof Array) {
			for (var i = 0; i < hs.length; i++) {
				if (hs[i] == n) return true;
			}
			return false;
		} else if (typeof(hs) == "string") {
			return !!hs.match(RegExp(n));
		} else if (typeof(hs) == "object") {
			return hs[n] !== undefined;
		} else {
			throw new TypeError("containment is undefined: " + n + " in " + JSON.stringify(hs));
		}
	}""", include='utils'),

	"strjoin": function("""function() {
		var buf = [];
		for (var i = 0; i < arguments.length; i++) {
			buf.push(arguments[i].toString());
		}
		return buf.join("");
	}""", include='utils'),

	"strmul": function("""function(s, n) {
		var buf = [];
		for (var i = 0; i < n; i++) {
			buf.push(s);
		}
		return buf.join('');
	}""", include='utils')
}
