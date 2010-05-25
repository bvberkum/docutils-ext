Error-Handling in docutils 
-------------------------------

Some Du reporter constructs.

::

    <paragraph>
        Unterminated 
        <problematic ids="id4" refid="id3">
            `
        inline test
    <system_message backrefs="id4" ids="id3" level="2" line="30" source="examples/errors.rst" type="WARNING">
        <paragraph>
            Inline interpreted text or phrase reference start-string without end-string.


::

    <system_message level="3" line="103" source="examples/form.rst" type="ERROR">
        <paragraph>
            Unexpected indentation.
    <block_quote>
        <paragraph>
            x


::

    <section classes="system-messages">
        <title>
            Docutils System Messages


Nicer formatting..
::

    <*:Element classes="form-field">
        <*:TextElement>
            Label text:
        <*:Element>
            <paragraph>
                <problematic:Inline>
                    Field value.
            <paragraph classes='form-help'>
                Enter a non-negative integer.
            <>

    <*:Element classes="system-messages form-messages">
        <system_message level=3 type=ERROR>
            Invalid literal for int() with base 10: 'd'.
            

(ERROR/3) invalid value 'My unsigned integer' for field `<field_body><paragraph>d</paragraph></field_body>`:

        invalid literal for int() with base 10: 'd'

My unsigned integer

d

