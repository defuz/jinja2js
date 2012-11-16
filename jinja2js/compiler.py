# -*- coding: utf-8 -*-
from StringIO import StringIO
from contextlib import contextmanager

from jinja2 import nodes
from jinja2.visitor import NodeVisitor
from jinja2.exceptions import TemplateAssertionError


class CodeGenerator(NodeVisitor):

	def __init__(self, stream):
		self.stream = stream or StringIO()
		self.indentation = 0

	def indent(self):
		self.indentation += 1

	def outdent(self, step=1):
		self.indentation -= step

	def write(self, x, *args):
		self.stream.write('    ' * self._indentation)
		self.stream.write(x % args)

	def line(self, x, *args):
		self.write(x + '\n', *args)

	def stmt(self, x, *args):
		self.line(x + ';', *args)

	def begin(self, x, *args):
		self.line(x + ' {', *args)
		self.indent()

	def end(self, x='}', *args):
		self.outdent()
		self.line(x, args)

	@contextmanager
	def block(self, x, *args):
		self.begin(x, *args)
		yield
		self.end()


class JSScope(object):

	def __init__(self):
		self.templates = set()
		self.depended_templates = set()


class JSCodeGenerator(CodeGenerator, NodeVisitor):

	def __init__(self, environment, scope=None, stream=None):
		super(JSCodeGenerator, self).__init__(stream)
		self.environment = environment
		self.scope = scope or JSScope()

	def begin_scope(self, stream):
		self.stmt('var Jinja = Jinja || {}')
		self.begin('(function(Jinja)')
		self.stmt('Jinja.templates = Jinja.templates || {}')

	def add_template(self, name, filename, node):
		if not isinstance(node, nodes.Template):
			raise TypeError('Can\'t compile non template nodes')
		self.name = name
		self.filename = filename
		self.visit(node)

	def end_scope(self, stream):
		self.end('}(Jinja));')

	def fail(self, msg, lineno):
		raise TemplateAssertionError(msg, lineno, self.name, self.filename)

	## VISITORS ##

	# todo: write all here :-P
