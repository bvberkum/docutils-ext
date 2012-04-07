| Line blocks are useful for addresses,
| verse, and adornment-free lists.
|
| Each new line begins with a
| vertical bar ("|").

|    Line breaks and initial indents
|    are preserved. (not, see Issues.rst)

| Continuation lines are wrapped
  portions of long lines; they begin
  with spaces in place of vertical bars.

:field: | line 1
        | line 2

:field:
  | line 1
  | line 2

block
  | block line 1
  | block line 2
    and still in line 2..

