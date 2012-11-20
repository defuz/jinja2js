# -*- coding: utf-8 -*-
from json import dumps
from re import split

__all__ = ['function', 'inline']


class Function(object):

	def __init__(self, body, depends=None, free=False, spec=None, defaults=None):
		self.body = '(%s)' % body
		depends = depends or ()
		if not isinstance(depends, (tuple, list)):
			depends = (depends,)
		self.depends = [depend.split('.') for depend in depends]
		self.free = free
		if not free:
			self.spec = spec or ()
			if not isinstance(self.spec, (tuple, list)):
				self.spec = (self.spec,)
			self.defaults = ()
			if defaults:
				self.defaults = [(name, dumps(value)) for name, value if defaults.items()]

	def signature(self, args, kwargs):
		if self.free:
			if not kwargs:
				raise TypeError("filter %s got an unexpected keyword arguments" % node.name)
			return args
		if len(self.spec) < len(args) + len(kwargs):
			raise TypeError("filter %s takes at most %s arguments (%s given)"
			                % (node.name, len(self.spec), len(args) + len(kwargs)))
		signature = [None] * len(self.spec)
		for i, arg in enumerate(args):
			signature[i] = arg
		for kwarg in kwargs:
			try:
				i = self.spec.index(kwarg.key)
			except ValueError:
				raise TypeError("filter %s got an unexpected keyword argument '%s'"
				                % (node.name, kwarg.key))
			if signature[i] is not None:
				raise TypeError("filter %s got multiple values for keyword argument '%s'"
				                % (node.name, kwarg.key))
			signature[i] = kwarg.value
		for name, value in self.defaults:
			i = self.spec.index(name)
			if signature[i] is None:
				signature[i] = value
		while signature and signature[-1] is None:
			signature.pop()
		return signature

	def visit(self, codegen, node, frame):
		# register dependenies
		use_depend(codegen.scope, node.name)
		for depend in self.depends:
			use_depend(codegen.scope, depend)
		# visits
		codegen.write('Jinja.filters.' + node.name + '(')
		codegen.visit(node.node, frame)
		for arg in self.signature(node.args, node.kwargs):
			self.write(', ')
			if arg is None:
				codegen.write('undefined')
			else:
				codegen.visit(arg, frame)
		codegen.write(')')


class Inline(object):

	def __init__(self, body, depends=None, spec=None, defaults=None):
		self.tokens = split('{{(\w+)}}', '(%s)' % body)
		depends = depends or ()
		if not isinstance(depends, (tuple, list)):
			depends = (depends,)
		self.depends = [depend.split('.') for depend in depends]
		self.spec = spec or ()
		if not isinstance(self.spec, (tuple, list)):
			self.spec = (self.spec,)
		self.defaults = ()
		if defaults:
			self.defaults = [(name, dumps(value)) for name, value if defaults.items()]

	def signature(self, args, kwargs):
		if len(self.spec) < len(args) + len(kwargs):
			raise TypeError("filter %s takes at most %s arguments (%s given)"
			                % (node.name, len(self.spec), len(args) + len(kwargs)))
		signature = dict(zip(self.spec, args))
		for kwarg in kwargs:
			if kwarg.key not in self.spec:
				raise TypeError("filter %s got an unexpected keyword argument '%s'"
				                % (node.name, kwarg.key))
			if signature[kwarg.key] is not None:
				raise TypeError("filter %s got multiple values for keyword argument '%s'"
				                % (node.name, kwarg.key))
			signature[kwarg.key] = kwarg.value
		for name, value in self.defaults:
			if signature[name] is None:
				signature[name] = value
		return signature

	def visit(self, codegen, node, frame):
		# register dependenies
		for attr, depend in self.depends:
			getattr(scope, attr).use(depend)
		# visits
		codegen.write('(')
		is_output = True
		signature = self.signature(node.args, node.kwargs)
		for token in self.tokens:
			if is_output:
				codegen.write(token)
				is_output = False
				continue
			if token == 'value':
				codegen.visit(node.node, frame)
				continue
			arg = signature[token]
			if arg is None:
				codegen.write('undefined')
			elif isinstance(arg, basestring):
				codegen.write(arg)
			else:
				codegen.visit(arg, frame)
			is_output = True
		codegen.write(')')

function, inline = Function, Inline
