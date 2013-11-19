# dotmpe docutils extension Makefile rules
#
include                $(MK_SHARE)Core/Main.dirstack.mk
MK                  += $/Rules.mk
#      ------------ -- 

PACK := docutils-ext.mpe


# Set targets to create documentation upon build
PIC_$d 				:= $(wildcard $/doc/*.pic)
PIC_PNG_$d 			:= $(PIC_$d:$/%.pic=$B%.png)
PIC_SVG_$d 			:= $(PIC_$d:$/%.pic=$B%.png)

RST_$d				:= $(wildcard $/*.rst $/doc/*.rst)
#XML_$d				:= $(RST_$d:$/%.rst=$B%.xml)
XHT_$d				:= $(RST_$d:$/%.rst=$B%.xhtml)

$(XHT_$d)  $(XML_$d)  $(PIC_PNG_$d)  $(PIC_SVG_$d) : $/Rules.mk

SRC                 += \
					   $(PIC_$d) \
					   $(RST_$d)
TRGT				+= \
					   $(XHT_$d) \
					   $(XML_$d) \
					   $(PIC_PNG_$d) \
					   $(PIC_SVG_$d)
CLN 				+= \
					   $(XHT_$d) \
					   $(XML_$d) \
					   $(PIC_PNG_$d) \
					   $(PIC_SVG_$d) \
					   $(shell find ./test ./dotmpe -iname '*.pyc')


#$B%.xml: $/%.rst    
#	@-./dotmpe-doctree.py --traceback $< $@ 
#	@-tidy -q -xml -utf8 -w 0 -i -m $@
#
#$B%.xhtml: $/%.rst    
#	@-./dotmpe-doc.py -d -t -g --link-stylesheet --stylesheet=/style/default $< $@  
#	@-tidy -q -xml -utf8 -w 0 -i -m $@
#
#clean: clean-pyc
#	@-rm README.xml README.xhtml
#
#clean-pyc:
#	@-find ./ -iname "*.pyc" | while read c; do rm "$$c"; done;

# XXX: convert this to test-python, see e.g. scrow
test:: test-validate-files
	@-test_listing=test/main.list;\
		test_mods=$$(cat $$test_listing|grep -v '^#'|grep -v '^$$');\
		test_listing=$$test_listing coverage run test/main.py $$test_mods \
		             2> test.log
	@coverage report --include="test/*,dotmpe/*"
	@if [ -n "$$(tail -1 test.log|grep OK)" ]; then \
	    $(ll) Success "$@" "see" test.log; \
	else \
	    $(ll) Errors "$@" "$$(tail -1 test.log)"; \
	    $(ll) Errors "$@" see test.log; \
	fi
	@\
	L=$$(ls var/|grep \.log);\
		[ "$$(echo $$L|wc -w)" -gt 0 ] && { $(ll) Errors "$@" "in testfiles" "$$(echo $$L)"; } || {}

#test-atlassian
test-common::
	@\
	    python test/main.py common
#test-rstwriter
test-form::
	@\
		python tools/rst-form.py examples/form.rst

TEST_RST_$d      := $(wildcard var/test-rst.*.rst)
TEST_RST_XML_$d  := $(TEST_RST_$d:%.rst=%.xml)

test-validate-files: $(TEST_RST_XML_$d)
	@\
		$(ll) attention "$@" "All XML files built, removing valid ones. "; \
		for x in var/*.xml; do echo $$x; stat $$x.*.log > /dev/null 2> /dev/null || rm $$x ; done;
	@\
	L=$$(ls var/|grep \.log);\
		[ "$$(echo $$L|wc -w)" -gt 0 ] && { $(ll) Errors "$@" "in testfiles" "$$(echo $$L)"; } || { $(ll) OK "$@"; }

var/%.xml: var/%.rst
	@\
	$(ll) file_target "$@" "Generating.." "$^" ;\
	./tools/rst2xml "$<" | tidy -w 0 -i -xml -q > "$@" 2> "$@.du.log"; \
	[ -s "$@.du.log" ] && { \
		$(ll) file_error "$@" "Warnings, see" $@.du.log; \
	} || { \
		rm "$@.du.log"; \
		xmllint --valid --noout $@ 2> $@.dtd.log; \
		[ -s "$@.dtd.log" ] && { \
		  $(ll) file_error "$@" "DTD validation warnings, see" "$@.dtd.log"; \
		} || { \
		  rm "$@.dtd.log"; \
		  $(ll) file_ok "$@"; \
		} \
	}

define build-pretty
	$(ll) file_target "$@" "Generating.." "$^" ;\
	./tools/rst2pprint "$<" "$@" 2> "$@.log" ;\
	[ -s "$@.log" ] && { \
		$(ll) file_error "$@" "Warnings, see" test.log; \
	} || { \
		rm "$@.log"; \
		$(ll) file_ok "$@"; \
	}
endef

var/%.pxml: var/%.rst
	@\
	$(build-pretty)

var/%.pxml: var/%.txt
	@\
	$(build-pretty)

#      ------------ -- 
include                $(MK_SHARE)Core/Main.dirstack-pop.mk
# vim:noet:
