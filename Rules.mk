include                $(MK_SHARE)Core/Main.dirstack.mk

MK                  += $/Rules.mk



RST_$d := $(wildcard $/*.rst $/doc/*.rst)
#XML_$d := $(RST_$d:$/%.rst=$B%.xml)
XHT_$d := $(RST_$d:$/%.rst=$B%.xhtml)
TRGT := $(XHT_$d) $(XML_$d)

#.PHONY: build clean clean-pyc test
#
#
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
#
#test:
#	python test/main.py




#      ------------ -- 
# ^3   ------------ --        ------------ -- # 1    ------------ -- 
# ^2   ------------ -- # 1    ------------ -- 
# 6    ----------------------------------- -- 
# 5    ------------------------------- -- 
# 4    --------------------------- -- 
# 3    ----------------------- -- 
# 2    ------------------- -- 
# 1    ------------ -- 
# -1   -------- -- 
# -2   ---- -- 
# -2    -- 
include                $(MK_SHARE)Core/Main.dirstack-pop.mk
# vim:noet:
