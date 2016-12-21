from dotmpe.du import form
from dotmpe.du.ext.transform import form1

import mpe


class Reader(mpe.Reader):

    """
    Reader with many transforms in priority range of 20 to 900.
    """

    settings_spec = (
        'Form Reader', None,
        form.FormProcessor.settings_spec
        + mpe.Reader.settings_spec[2]
    )

    def get_transforms(self):
        #return standalone.Reader.get_transforms(self) + [
        return mpe.Reader.get_transforms(self) + [
            form1.DuForm
        ]


