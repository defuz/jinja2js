# -*- coding: utf-8 -*-

utils = {
	"extend": """function(base, child) {
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
	}""",

	"slice": """function(val, start, stop) {
		if (typeof(val) == "string") {
			return val.substring(start, stop);
		} else if (val instanceof Array) {
			return val.slice(start, stop);
		}
	}""",

	"loop": """function(iter) {
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
	}""",

	"contains": """function(n, hs) {
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
	}""",

	"strjoin": """function() {
		var buf = [];
		for (var i = 0; i < arguments.length; i++) {
			buf.push(arguments[i].toString());
		}
		return buf.join("");
	}""",

	"strmul": """function(s, n) {
		var buf = [];
		for (var i = 0; i < n; i++) {
			buf.push(s);
		}
		return buf.join('');
	}"""
}
