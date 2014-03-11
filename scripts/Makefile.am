MAINTAINERCLEANFILES = Makefile.in

install-exec-local:
	install -m 755 ./rich-core-dumper $(DESTDIR)/usr/sbin

install-data-local:
	install -m 644 ./rich-core-early-collect.service $(DESTDIR)/lib/systemd/system
	ln -s ../rich-core-early-collect.service $(DESTDIR)/lib/systemd/system/basic.target.wants/rich-core-early-collect.service

libexec_SCRIPTS = \
	rich-core-check-oneshot
