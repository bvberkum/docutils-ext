d = .
RST_$d := $(wildcard $d/*.rst)
XML_$d := $(RST_$d:%.rst=%.xml)
XHT_$d := $(RST_$d:%.rst=%.xhtml)
TRGT := $(XHT_$d) $(XML_$d)

.PHONY: build clean clean-pyc test

build: $(TRGT)

$d/%.xml: $d/%.rst    
	@-./dotmpe-doctree.py --traceback $< $@ 
	@-tidy -q -xml -utf8 -w 0 -i -m $@

$d/%.xhtml: $d/%.rst    
	@-./dotmpe-doc.py -d -t -g --link-stylesheet --stylesheet=/style/default $< $@  
	@-tidy -q -xml -utf8 -w 0 -i -m $@

clean: clean-pyc
	@-rm README.xml README.xhtml

clean-pyc:
	@-find ./ -iname "*.pyc" | while read c; do rm "$$c"; done;

test:
	python test/main.py
