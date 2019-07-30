# Makefile.am
#   Automake makefile for atftp
#
# $Id: Makefile.am,v 1.15 2004/03/16 01:37:24 jp Exp $
#
# Copyright (c) 2001 Jean-Pierre Lefebvre <helix@step.polymtl.ca>
#                and Remi Lefebvre <remi@debian.org>
#
# atftp is free software; you can redistribute them and/or modify them
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later

AUTOMAKE_OPTIONS = foreign
SUBDIRS          = . test
DIST_SUBDIRS     = $(SUBDIRS)
CLEANFILES       = *~
DISTCLEANFILES   = libtool PLATFORM
AM_CPPFLAGS      = -D_GNU_SOURCE

man_MANS         = atftp.1 atftpd.8
dist_scripts     = autogen.sh
dist_docs        = BUGS Changelog FAQ LICENSE README.CVS README.MCAST README.PCRE
dist_dirs        = test redhat docs debian
EXTRA_DIST       = $(dist_docs) $(dist_dirs) $(man_MANS) $(dist_scripts)

noinst_HEADERS   = argz.h logger.h options.h stats.h tftp.h tftp_def.h tftp_io.h \
		   tftpd.h tftpd_pcre.h tftpd_mtftp.h

bin_PROGRAMS     = atftp
atftp_LDADD      = $(LIBTERMCAP) $(LIBREADLINE)
atftp_SOURCES    = tftp.c tftp_io.c logger.c options.c tftp_def.c tftp_file.c \
		   argz.c tftp_mtftp.c

sbin_PROGRAMS    = atftpd
atftpd_LDADD     = $(LIBWRAP) $(LIBPTHREAD) $(LIBPCRE)
atftpd_SOURCES   = tftpd.c logger.c options.c stats.c tftp_io.c tftp_def.c \
                   tftpd_file.c tftpd_list.c tftpd_mcast.c argz.c tftpd_pcre.c \
		   tftpd_mtftp.c

install-exec-hook:
	(cd $(DESTDIR)$(sbindir) && ln -sf atftpd in.tftpd)

install-data-hook:
	(cd $(DESTDIR)$(mandir)/man8 && ln -sf atftpd.8 in.tftpd.8)

uninstall-local:
	rm -f $(DESTDIR)$(sbindir)/in.tftpd $(DESTDIR)$(mandir)/man8/in.tftpd.8

dist-hook:
	cd $(distdir) && rm -rf `find . -type d -name CVS`
