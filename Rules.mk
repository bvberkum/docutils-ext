include                $(MK_SHARE)Core/Main.dirstack.mk

MK                  += $/Rules.mk


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
					   $(PIC_SVG_$d)


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
test::
	python test/main.py




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
