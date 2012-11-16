# -*- coding: utf-8 -*-

FILTER_ARGS = {
	'attr': ('name',),
	'batch': ('linecount', 'fill_with'),
	'center': ('width',),
	'default': ('default_value', 'boolean'),
	'd': ('default_value', 'boolean'),
	'dictsort': ('case_sensitive', 'by'),
	'filesizeformat': ('binary',),
	'float': ('default',),
	'groupby': ('attribute',),
	'indent': ('width', 'indentfirst'),
	'int': ('default',),
	'join': ('d', 'attribute'),
	'replace': ('old', 'new', 'count'),
	'round': ('precision', 'method'),
	'slice': ('slices', 'fill_with'),
	'sort': ('reverse', 'case_sensitive', 'attribute'),
	'sum': ('attribute', 'start'),
	'truncate': ('length', 'killwords', 'end'),
	'xmlattr': ('autospace',),
}



