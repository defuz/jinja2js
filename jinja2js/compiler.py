# -*- coding: utf-8 -*-
from StringIO import StringIO
from copy import deepcopy
from json import dumps

from jinja2 import nodes
from jinja2.optimizer import optimize
from jinja2.visitor import NodeVisitor
from jinja2.compiler import Frame as _Frame, EvalContext
from jinja2.exceptions import TemplateAssertionError

from filters import filters, filter_args
from tests import tests
from utils import utils


def _get_template(env, name=None, source=None):
	if name:
		source, filename, _ = env.loader.get_source(env, name)
	else:
		name, filename = '<template>', '<template>'
	ast = env._parse(source, name, filename)
	if env.optimized:
		ast = optimize(ast, env)
	return name, filename, ast


class Functions(object):

	def __init__(self):
		self.declared = set()
		self.undeclared = set()

	def use(self, name):
		if name not in self.declared:
			self.undeclared.add(name)

	@property
	def for_declaration(self):
		while self.undeclared:
			x = self.undeclared.pop()
			self.declared.add(x)
			yield x

	def copy(self):
		return deepcopy(self)


class Scope(object):

	def __init__(self):
		self.templates = Functions()
		self.filters = Functions()
		self.tests = Functions()
		self.utils = Functions()

	def copy(self):
		return deepcopy(self)


class Frame(_Frame):

	def special_name(self, prefix):
		idx, n = 0, prefix + '0'
		while n in self.identifiers.declared:
			idx, n = idx + 1, prefix + str(idx + 1)
		return n


class CodeGenerator(NodeVisitor):

	def __init__(self, environment, scope=None, stream=None):
		self.environment = environment
		self.scope = scope or Scope()
		self.stream = stream or StringIO()
		self.indentation = 0
		self.new_line = True

	def generate(self, templates=None, source=None):
		self.line('var Jinja = Jinja || {templates:{}, filters:{}, tests:{}, utils:{}};')
		self.begin('(function(Jinja) {')
		if source:
			self.generate_template(source=source)
		if templates:
			for name in templates:
				self.generate_template(name=name)
		for name in self.scope.templates.for_declaration:
			self.generate_template(name=name)
		for name in self.scope.filters.for_declaration:
			self.generate_filter(name)
		for name in self.scope.tests.for_declaration:
			self.generate_test(name)
		for name in self.scope.utils.for_declaration:
			self.generate_utils(name)
		self.end('}(Jinja));')

	def generate_template(self, name=None, source=None):
		name, filename, ast = _get_template(self.environment, name, source)
		if not isinstance(ast, nodes.Template):
			raise TypeError('Can\'t compile non template nodes')
		self.name = name
		self.filename = filename
		self.visit(ast)

	def generate_filter(self, name):
		if name not in filters:
			raise TypeError('Can\'t find javascript realization of filter %s' % name)
		self.line('Jinja.filters.%s = (%s);' % (name, filters[name]))

	def generate_test(self, name):
		if name not in tests:
			raise TypeError('Can\'t find javascript realization of test %s' % name)
		self.line('Jinja.tests.%s = (%s);' % (name, tests[name]))

	def generate_utils(self, name):
		if name not in utils:
			raise TypeError('Can\'t find javascript realization of %s' % name)
		self.line('Jinja.utils.%s = (%s);' % (name, utils[name]))

	## shortcuts ##

	def indent(self):
		self.indentation += 1

	def outdent(self, step=1):
		self.indentation -= step

	def write(self, x):
		self.stream.write(x)
		self.new_line = False

	def line(self, x):
		if not self.new_line:
			self.write('\n')
		self.write('    ' * self.indentation + x + '\n')
		self.new_line = True

	def begin(self, x):
		self.line(x)
		self.indent()

	def end(self, x):
		self.outdent()
		self.line(x)

	def fail(self, msg, lineno):
		raise TemplateAssertionError(msg, lineno, self.name, self.filename)

	## visitors ##

	def jsmacro(self, node, frame):

		self.write('"%s": function(ctx, tmpl' % node.name)

		args = set()
		for n in node.args:
			self.write(', ')
			self.write(n.name)
			args.add(n.name)

		frame = Frame(frame.eval_ctx, frame)
		frame.identifiers.declared = args
		self.begin(') {')

		for arg, val in zip(node.args[-len(node.defaults):], node.defaults):
			self.visit(arg, frame)
			self.write(' = ')
			self.visit(arg, frame)
			self.write(' || ')
			self.visit(val, frame)
			self.write(';')

		self.line('var %s = [];' % frame.buffer)
		for n in node.body:
			self.visit(n, frame)

		self.line('return %s.join("");' % frame.buffer)
		self.end('}')

	def block(self, node, frame):

		self.begin('"%s": function(ctx) {' % node.name)
		self.line('var %s = [];' % frame.buffer)

		frame = Frame(frame.eval_ctx, frame)
		for n in node.body:
			self.visit(n, frame)

		self.line('return %s.join("");' % frame.buffer)
		self.end('}')

	def visit_Include(self, node, frame):
		self.scope.templates.use(node.template)
		self.write('%s.push(Jinja.templates[' % frame.buffer)
		self.visit(node.template, frame)
		self.write('].render(ctx));')

	def visit_Template(self, node, frame=None):

		frame = Frame(EvalContext(self.environment, self.name))
		frame.buffer = '_buf'
		frame.toplevel = True

		self.begin('Jinja.templates["%s"] = {' % self.name)
		self.write('"macros": ')
		macros = list(node.find_all(nodes.Macro))
		if not macros:
			self.write('{},')
		else:
			self.begin('{')
			for i, n in enumerate(macros):
				self.jsmacro(n, frame)
				if i != len(macros) - 1:
					self.write(',')
			self.end('},')

		self.write('"blocks": ')
		blocks = list(node.find_all(nodes.Block))
		if not blocks:
			self.write('{},')
		else:
			self.begin('{')
			for i, n in enumerate(blocks):
				self.block(n, frame)
				if i != len(blocks) - 1:
					self.write(',')
			self.end('},')

		self.begin('"render": function(ctx, tmpl) {')

		extends = node.find(nodes.Extends)
		if extends:
			self.scope.templates.use(extends.template)
			self.write('return Jinja.templates[')
			self.visit(extends.template, frame)
			self.write('].render(ctx, this);')
		else:
			self.scope.utils.use('extend')
			self.line('tmpl = Jinja.utils.extend(this, tmpl);')
			self.line('var %s = [];' % frame.buffer)
			for n in node.body:
				self.visit(n, frame)
			self.line('return %s.join("");' % frame.buffer)

		self.end('}')
		self.end('};')

	def visit_Const(self, node, frame):
		val = node.value
		if isinstance(val, float):
			self.write(str(val))
		elif val is False:
			self.write('false')
		elif val is True:
			self.write('true')
		elif val is None:
			self.write('null')
		else:
			self.write(dumps(val))

	def visit_Tuple(self, node, frame):
		self.visit_List(node, frame)

	def visit_Block(self, node, frame):
		bits = frame.buffer, node.name
		self.line('%s.push(tmpl.blocks["%s"](ctx));' % bits)

	def visit_Extends(self, node, frame):
		pass

	def visit_Macro(self, node, frame):
		pass

	def visit_FilterBlock(self, node, frame):

		local = Frame(EvalContext(self.environment, self.name))
		local.buffer = '_fbuf'
		local.toplevel = frame.toplevel

		self.line('var %s = [];' % local.buffer)
		for n in node.body:
			self.visit(n, local)

		bits = frame.buffer, node.filter.name, local.buffer
		self.scope.filters.use(node.filter.name)
		self.line('%s.push(Jinja.filters.%s(%s.join("")));' % bits)

	def visit_Assign(self, node, frame):

		if isinstance(node.target, nodes.Tuple):
			for target in node.target.items:
				frame.identifiers.declared.add(target.name)
		else:
			frame.identifiers.declared.add(node.target.name)

		self.write('var ')
		self.visit(node.target, frame)
		self.write(' = ')
		self.visit(node.node, frame)
		self.write(';')

	def visit_Call(self, node, frame):

		if isinstance(node.node, nodes.Name):
			self.write('tmpl.macros.' + node.node.name)
			self.write('(ctx, tmpl')
			if node.args:
				self.write(', ')
		else:
			self.visit(node.node, frame)
			self.write('(')

		if not node.args:
			self.write(')')
			return

		first = True
		for n in node.args:
			if not first:
				self.write(', ')
			self.visit(n, frame)
			first = False
		self.write(')')

	def visit_Output(self, node, frame):
		for n in node.nodes:
			self.write('%s.push(' % frame.buffer)
			self.visit(n, frame)
			self.write(');')

	def visit_Name(self, node, frame):
		if node.name in frame.identifiers.declared:
			self.write(node.name)
		else:
			self.write('ctx.%s' % node.name)

	def visit_TemplateData(self, node, frame):
		val = node.as_const(frame.eval_ctx)
		self.write(dumps(val))

	def visit_CondExpr(self, node, frame):
		self.write('(')
		self.visit(node.test, frame)
		self.write(' ? ')
		self.visit(node.expr1, frame)
		self.write(' : ')
		self.visit(node.expr2, frame)
		self.write(')')

	def visit_Getattr(self, node, frame):
		self.visit(node.node, frame)
		self.write('.')
		self.write(node.attr)

	def visit_Getitem(self, node, frame):
		if isinstance(node.arg, nodes.Slice):

			assert node.arg.step is None
			self.scope.utils.use('slice')
			self.write('Jinja.utils.slice(')
			self.visit(node.node, frame)
			self.write(', ')

			if node.arg.start is not None:
				self.visit(node.arg.start, frame)
			else:
				self.write('0')

			self.write(', ')
			if node.arg.stop is not None:
				self.visit(node.arg.stop, frame)
			else:
				self.write('undefined')

			self.write(')')

		else:
			self.visit(node.node, frame)
			self.write('[')
			self.visit(node.arg, frame)
			self.write(']')

	def for_targets(self, node, loopvar, frame, pre=''):

		if isinstance(node, nodes.Tuple):
			for i, target in enumerate(node.items):
				frame.identifiers.declared.add(target.name)
				self.write('var ')
				self.visit(target, frame)
				bits = pre + loopvar, pre + loopvar, i
				self.write(' = %s.iter[%s.i][%s];' % bits)
		else:
			frame.identifiers.declared.add(node.name)
			self.write('var ')
			self.visit(node, frame)
			self.write(' = %s.iter[%s.i];' % (pre + loopvar, pre + loopvar))

	def visit_For(self, node, frame):

		before = frame.identifiers.declared.copy()
		loopvar = frame.special_name('_loopvar')
		if loopvar.endswith('0') and 'loop' in frame.identifiers.declared:
			self.line('var _pre_loop = loop;')

		frame.identifiers.declared.add(loopvar)
		frame.identifiers.declared.add('loop')
		if node.test:
			self.scope.utils.use('loop')
			self.write('var f%s = Jinja.utils.loop(' % loopvar)
			self.visit(node.iter, frame)
			self.write(');')

			vars = (loopvar,) * 4
			self.line('var g%s = [];' % loopvar)
			self.begin('for (f%s.i = 0; f%s.i < f%s.l; f%s.i++) {' % vars)

			self.for_targets(node.target, loopvar, frame, 'f')
			self.write('if (!')
			self.visit(node.test, frame)
			self.write(') continue;')

			bits = (loopvar,) * 3
			self.write('g%s.push(f%s.iter[f%s.i]);' % bits)
			self.end('}')

		self.scope.utils.use('loop')
		self.write('var %s = Jinja.utils.loop(' % loopvar)
		if not node.test:
			print '?????????????????'
			print node.iter
			self.visit(node.iter, frame)
		else:
			self.write('g%s' % loopvar)
		self.write(');')

		vars = (loopvar,) * 4
		self.begin('for (%s.i = 0; %s.i < %s.l; %s.i++) {' % vars)

		self.for_targets(node.target, loopvar, frame)
		self.line('loop = %s;' % loopvar)
		self.line('loop.update();')

		for n in node.body:
			self.visit(n, frame)

		self.end('}')
		if loopvar[8:] != '0':
			self.line('loop = _loopvar%s;' % (int(loopvar[8:]) - 1))

		frame.identifiers.declared = before
		if loopvar.endswith('0') and 'loop' in frame.identifiers.declared:
			self.line('loop = _pre_loop;')

	def visit_Filter(self, node, frame):
		self.scope.filters.use(node.name)
		self.write('Jinja.filters.' + node.name + '(')
		self.visit(node.node, frame)

		if not node.args and not node.kwargs:
			self.write(')')
			return

		if node.args and not node.kwargs:
			for n in node.args:
				self.write(', ')
				self.visit(n, frame)
			self.write(')')
			return

		spec = dict((k, i) for (i, k) in enumerate(filter_args[node.name]))
		args = [None] * (len(spec))
		for i, arg in enumerate(node.args):
			args[i] = arg
		for arg in node.kwargs:
			args[spec[arg.key]] = arg.value
		while args and args[-1] is None:
			args.pop()

		for n in args:
			self.write(', ')
			if n is None:
				self.write('undefined')
			else:
				self.visit(n, frame)
		self.write(')')

	def visit_Test(self, node, frame):
		self.scope.tests.use(node.name)
		self.write('Jinja.tests.' + node.name + '(')
		self.visit(node.node, frame)
		self.write(')')

	def visit_Not(self, node, frame):
		self.write('!')
		self.visit(node.node, frame)

	def visit_Concat(self, node, frame):
		self.scope.utils.use('strjoin')
		self.write('Jinja.utils.strjoin(')
		first = True
		for n in node.nodes:
			if not first:
				self.write(', ')
			self.visit(n, frame)
			first = False
		self.write(')')

	def visit_If(self, node, frame):

		self.write('if (')
		self.visit(node.test, frame)
		self.begin(') {')

		for n in node.body:
			self.visit(n, frame)

		if not node.else_:
			self.end('}')
			return

		self.outdent()
		self.line('} else {')
		self.indent()

		for n in node.else_:
			self.visit(n, frame)
		self.end('}')

	def visit_Compare(self, node, frame):

		if node.ops[0].op not in ('in', 'notin'):
			self.visit(node.expr, frame)
			for op in node.ops:
				self.visit(op, frame)
			return

		oper = node.ops[0]
		if oper.op == 'notin':
			self.write('!')
		self.scope.utils.use('contains')
		self.write('Jinja.utils.contains(')
		self.visit(node.expr, frame)
		self.write(', ')
		self.visit(oper.expr, frame)
		self.write(')')

	def binop(op):
		def visitor(self, node, frame):
			self.write('(')
			self.visit(node.left, frame)
			self.write(' %s ', op)
			self.visit(node.right, frame)
			self.write(')')
		return visitor

	visit_And = binop('&&')
	visit_Or = binop('||')
