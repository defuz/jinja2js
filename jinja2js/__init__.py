# -*- coding: utf-8 -*-
from jinja2.ext import Extension

from compiler import CodeGenerator

__version__ = '0.1-aplha'


class Jinja2JS(Extension):

	def __init__(self, env):
		self.bind(env)

	def bind(self, env):
		def compile_js(templates=None, source=None,
		               scope=None, stream=None,
		               extensions=None, filter_func=None):
			if templates is None and source is None:
				templates = env.loader.list_templates(extensions, filter_func)
			generator = CodeGenerator(env, scope, stream)
			generator.generate(templates=templates, source=source)
			if stream is None:
				return generator.stream.getvalue()
		env.extend(compile_js=compile_js)


jinja2js = Jinja2JS
