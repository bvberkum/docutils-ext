from docutils import Component
from docutils.transforms import universal
import docutils.readers

from dotmpe.du.ext.transform import specinfo


class Reader(docutils.readers.Reader):

    """
    Reader with minimal settings_spec for SpecInfo support.
    """

    reader_settings_spec = (
            )

    settings_spec = (
            'SpecInfo reader',
            None,
            reader_settings_spec +
            specinfo.SpecInfo.settings_spec 
    )
    config_section = 'Specinfo reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        return Component.get_transforms(self) + [
#            universal.Decorations,
            universal.ExposeInternals,
#            universal.StripComments
            specinfo.SpecInfo,
            ]
