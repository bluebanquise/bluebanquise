dnl configure.in
dnl
dnl $Id: configure.ac,v 1.3 2004/03/16 01:51:40 jp Exp $
dnl
dnl Copyright (c) 2001 Jean-Pierre Lefebvre <helix@step.polymtl.ca>
dnl                and Remi Lefebvre <remi@debian.org>
dnl
dnl atftp is free software; you can redistribute them and/or modify them
dnl under the terms of the GNU General Public License as published by the
dnl Free Software Foundation; either version 2 of the License, or (at your
dnl option) any later version.

AC_INIT([atftp], [0.7.2])
AC_CONFIG_SRCDIR([tftp.c])
AM_INIT_AUTOMAKE

AC_SUBST(VERSION)
AM_CONFIG_HEADER(config.h)

ISODATE=`date +%Y-%m-%d`
AC_SUBST(ISODATE)

dnl canonicalize the host
AC_CANONICAL_HOST
dnl AC_CANONICAL_TARGET 
PLATFORM="${host_vendor}-${host_cpu}-${host_os}"
AC_SUBST(PLATFORM)

dnl Additional argument
AC_ARG_ENABLE(libreadline,
	[  --enable-libreadline    enable readline support in client],
	[ case "${enableval}" in
	        yes) libreadline=true ;;
		no) libreadline=false ;;
	  esac], [libreadline=true])

AC_ARG_ENABLE(libwrap,
	[  --enable-libwrap        enable libwrap support in server],
	[ case "${enableval}" in
		yes) libwrap=true ;;
		no) libwrap=false ;;
	  esac], [libwrap=true])

AC_ARG_ENABLE(libpcre,
	[  --enable-libpcre        enable libpcre support in server],
	[ case "${enableval}" in
		yes) libpcre=true ;;
		no) libpcre=false ;;
	  esac], [libpcre=true])

AC_ARG_ENABLE(mtftp,
	[  --enable-mtftp          enable mtftp support in server],
	[ case "${enableval}" in
		yes) mtftp=true ;;
		no) mtftp=false ;;
	  esac], [mtftp=true])

AC_ARG_ENABLE(debug,
	[  --enable-debug          enable debug code in server/client],
	[ case "${enableval}" in
		yes) debug=true ;;
		no)  debug=false ;;
	  esac], [debug=false])

dnl Check for programs
AC_PROG_CC
AC_GNU_SOURCE

dnl Check for AIX
AC_AIX

#CFLAGS="$CFLAGS -g -Wall -D_REENTRANT"

## JohnnyKeats fix to prevend gcc > 5.2 build crash

CFLAGS="$CFLAGS -std=gnu89 -fPIC -g -O2"
CFLAGS+=" -std=gnu89 -fPIC -g -O2"

#if test x$debug = xtrue; then
#   CFLAGS="$CFLAGS -O0 -DDEBUG"
#else
#  if test -n "$auto_cflags"; then
#    if test -n "$GCC"; then
#      CFLAGS="$CFLAGS -g -O2 -Wall -Wno-implicit"
#    else
#      case "$host_os" in
#        *hpux*)  CFLAGS="$CFLAGS +O3"
#	  ;;
#        *ultrix* | *osf*) CFLAGS="$CFLAGS -O -Olimit 2000"
#	  ;;
#        *)       CFLAGS="$CFLAGS -O2"
#	  ;;
#      esac
#    fi
#  else
#    CFLAGS="$CFLAGS -O2"
#  fi
#fi

AC_PROG_MAKE_SET
AC_PROG_INSTALL

dnl enable mtftp support
if test x$mtftp = xtrue; then
   AC_DEFINE([HAVE_MTFTP], 1, "Support MTFTP protocol")
fi

dnl Checks for libraries
dnl Thread support is needed in the server
AC_CHECK_LIB(pthread, pthread_create, [LIBPTHREAD=-lpthread],
		      [AC_MSG_ERROR(not found)])
AC_SUBST(LIBPTHREAD)

dnl If we want libreadline support
if test x$libreadline = xtrue; then
   dnl Debian's readline is already linked to ncurses. It is not the case for
   dnl all other systems.
   AC_CHECK_LIB(readline, tgetent, LIBTERMCAP="",
	AC_CHECK_LIB(ncurses, tgetent, LIBTERMCAP=-lncurses,
		AC_CHECK_LIB(curses, tgetent, LIBTERMCAP=-lcurses,
			AC_CHECK_LIB(termcap, tgetent, LIBTERMCAP=-ltermcap,
			AC_MSG_RESULT(no)))))
   AC_SUBST(LIBTERMCAP)

   dnl Check for readline
   AC_CHECK_LIB(readline, readline,
         [LIBREADLINE=-lreadline]
	 [AC_DEFINE([HAVE_READLINE], 1,
		"Support for readline in tftp client")],
	 AC_MSG_RESULT(no), $LIBTERMCAP)
   AC_SUBST(LIBREADLINE)

   dnl Verify readline has completion support (this function changes from
   dnl release to release :(
   AC_CHECK_LIB(readline, rl_completion_matches,
	     AC_DEFINE([HAVE_RL_COMPLETION_MATCHES], 1, "Use completion"),
	     AC_CHECK_LIB(readline, completion_matches,
		          AC_DEFINE([HAVE_COMPLETION_MATCHES], 1,
					"Use completion"),
		          AC_MSG_RESULT(no), $LIBTERMCAP),
	     $LIBTERMCAP)
fi

dnl If we want to compile libwrap stuff, check for libraries
if test x$libwrap = xtrue; then
   dnl Checking to libwrap. Some systems don't define default values for
   dnl allow_severity and deny_severity so we need a somewhat more complicated
   dnl test here. We automatically link against nsl since libwrap is not
   dnl already linked with it on all systems.
   orig_LIBS="$LIBS"
   LIBS="-lnsl -lwrap"
   AC_MSG_CHECKING([for hosts_ctl in -lwrap])
   AC_TRY_LINK([
        #include <tcpd.h>
        int allow_severity;
        int deny_severity;
        ],
	hosts_ctl("", STRING_UNKNOWN, STRING_UNKNOWN, STRING_UNKNOWN);
        ,
        LIBWRAP="-lnsl -lwrap"
        LIBS="$orig_LIBS"
        AC_MSG_RESULT(yes)
        AC_DEFINE([HAVE_WRAP], 1, "Support for libwrap")
        ,
        LIBWRAP=""
        LIBS="$orig_LIBS"
        AC_MSG_RESULT(no)
   )
   AC_SUBST(LIBWRAP)
fi

dnl If we want to compile pcre stuff, check for libraries
if test x$libpcre = xtrue; then
   dnl Checking to pcre.
   AC_CHECK_LIB(pcre, pcre_version,
	        [LIBPCRE=-lpcre]
		[AC_DEFINE([HAVE_PCRE], 1,
		"Support for libpcre pattern subsitution")])
   AC_SUBST(LIBPCRE)
fi

dnl Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS(sys/time.h sys/types.h sys/socket.h)
AC_CHECK_HEADERS(arpa/inet.h arpa/tftp.h)
AC_CHECK_HEADERS(getopt.h unistd.h signal.h pthread.h argz.h)
AC_CHECK_HEADERS(netdb.h)
AC_CHECK_HEADERS(readline/readline.h)
AC_CHECK_HEADERS(readline/history.h)
if test x$libwrap = xtrue; then
AC_CHECK_HEADERS(tcpd.h)
fi
if test x$libpcre = xtrue; then
AC_CHECK_HEADERS(pcre.h)
fi

dnl Checks for typedefs, structures, and compiler characteristics.
AC_C_CONST
AC_TYPE_SIZE_T
AC_HEADER_TIME
AC_TYPE_SIGNAL

dnl Checks for library functions.
AC_CHECK_FUNCS(strchr memcpy strstr strcmp strncmp strncpy strlen)
AC_CHECK_FUNCS(strncasecmp strcasecmp strncmp)
AC_CHECK_FUNCS(socket gethostbyname gethostbyname_r gethostbyaddr)

dnl Write platform to file for support reporting
AC_OUTPUT_COMMANDS([
	outfile=PLATFORM
	tmpfile=${outfile}
	cat > $tmpfile << _EOF_
$PLATFORM
_EOF_
], [PLATFORM=$PLATFORM])

AC_OUTPUT(Makefile test/Makefile redhat/atftp.spec)
