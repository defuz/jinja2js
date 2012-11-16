# -*- coding: utf-8 -*-
__version__ = '0.1-aplha'


class Jinja2JS(object):

	def __init__(self, env):
		self.bind(self, env)

	def bind(self, env):
		def compile_js(templates=None, stream=None, scope=None, extensions=None, filter_func=None):
			if templates is None:
				templates = env.loader.list_templates(extensions, filter_func)
			generator = JSCodeGenerator(env, scope, stream)
			generator.start_scope()
			for name in templates:
				source, filename, _ = env.loader.get_source(env, name)
				ast = env._parse(source, name, filename)
				if env.optimized:
					from jinja2.optimizer import optimize
					ast = optimize(ast, env)
				generator.generate_template(name, filename, ast)
			generator.end_scope()
			if stream is None:
				return generator.stream.getvalue()
		env.extend(generate_js=generate_js)
