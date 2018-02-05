
setup()
{
  TEST=var/test-rst.1.document-5.full-rst-demo.rst
  TEST=var/test-rst.24.references.rst
  export PYTHONPATH=.:$PYTHONPATH
}

@test "build.py can record outgoing refs, in todo.txt format" {

  python tools/rst2pprint \
    --traceback \
              --record-references=/tmp/ref.list \
              --record-reference-format=todo.txt \
              $TEST /dev/null
  test $(stat -f '%z' /tmp/ref.list) -eq 208

  test "$(cat /tmp/ref.list)" = "$(cat <<EOM
example-ref-name-1 <http://www.python.org/>
example-name-5 <http://www.python.org/> anonymous:1
example-name-5 <http://www.python.org/>
example-name-5 <http://www.python.org/>
Python <http://www.python.org/>
EOM
  )"
}


@test "build.py can record outgoing refs, in text format" {

  python tools/rst2pprint \
    --traceback \
              --record-references=/tmp/ref.out \
              --record-reference-format=text \
              $TEST /dev/null
  test $(stat -f '%z' /tmp/ref.out) -eq 175
  test "$(cat /tmp/ref.out)" = "$(cat <<EOM
http://www.python.org/  example-ref-name-1
http://www.python.org/
http://www.python.org/  example-name-5
http://www.python.org/  example-name-5
http://www.python.org/  Python
EOM
  )"
}
