"""
just some thoughts.
"""
from docutils import Component


class ReferenceResolver(Component):

	"""
	Compatible with document.transformer.unknown_reference_resolvers?
	Should this be a transform?
	See ContentResolver below.
	"""

# inhertied from SettingsSpec
#	settings_defaults = None
#	settings_default_overrides = None
#	relative_path_settings = ()
#	config_section = None
#	config_section_dependencies = None

# inherted from TransformSpec
#	def get_transforms(self):
#		return []

	def __call__(self, node):
		# transform reference node
		return True

	def resolve_reference(self, reference, remote=None):
		"Globalize reference from current document. "
		"Specify remote to also translate the reference to the other document. "


class ContentResolver(ReferenceResolver):

	"""
	In/Output factories. 
	Protocol layer to resolve based on Content-ID, Format, Language, Encoding?
	See README.
	"""

	component_type = 'resolver'
	config_section = 'resolvers'

	def read(self):
		"return all content"

	def write(self, data):
		"truncate and rewrite content"

	def stat(self):
		pass



_resolver_aliases = {
}

def get_resolver_class(resolver_name):
	pass
