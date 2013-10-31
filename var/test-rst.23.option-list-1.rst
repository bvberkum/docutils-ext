Option Lists
------------

For listing command-line options:

.. XXX: not supported yet
  -a            command-line option "a"
  -b file       options can have arguments
                and long descriptions
  --long        options can be long also
  --input=file  long options can also have
                arguments

  -x, -y, -z    Multiple options are an "option group".
  -v, --verbose  Usually we list one short & one long option.
                If the list of options gets to long, rSt still 
                parses it.
  --very-long-option
                The description can also start on the next line.

  -1 file, --one=file, --two file
                Multiple options with arguments.
  /V            DOS/VMS-style options too


..
              The description may contain multiple body elements,
              regardless of where it starts, and *inline* 
              `rSt <http://docutils.sourceforge.net>`_ **markup**
              too ofcourese::
                Even some block elements are fine..
              | To use within the description.  

There must be at least two spaces between the option and the
description.

