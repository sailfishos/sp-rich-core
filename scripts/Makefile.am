MAINTAINERCLEANFILES = Makefile.in

install-exec-local:
	install -m 755 ./rich-core-dumper $(DESTDIR)/usr/sbin
	mkdir -p $(DESTDIR)/usr/lib/startup/preinit/late.d
	install -m 755 ./rich-core-preinit $(DESTDIR)/usr/lib/startup/preinit/late.d

install-data-local:
	install -m 644 ./rich-core-early-collect.service $(DESTDIR)/lib/systemd/system
	mkdir -p $(DESTDIR)/lib/systemd/system/graphical.target.wants
	ln -s ../rich-core-early-collect.service \
		$(DESTDIR)/lib/systemd/system/graphical.target.wants/rich-core-early-collect.service

libexec_SCRIPTS = \
	rich-core-check-oneshot
