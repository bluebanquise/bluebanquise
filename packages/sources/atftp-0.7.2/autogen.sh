#!/bin/sh

AUTOCONF_REQUIRED_VERSION=2.5
AUTOMAKE_REQUIRED_VERSION=1.7

check_version ( ) {
    if [ "x$1" = "x" ] ; then
        echo "INTERNAL ERROR: check_version was not provided a minimum version"
        exit 1
    fi
    _min="$1"
    if [ "x$2" = "x" ] ; then
        echo "INTERNAL ERROR: version check was not provided a comparison version"
        exit 1
    fi
    _cur="$2"

    # needed to handle versions like 1.10 and 1.4-p6
    _min="`echo ${_min}. | sed 's/[^0-9]/./g' | sed 's/\.\././g'`"
    _cur="`echo ${_cur}. | sed 's/[^0-9]/./g' | sed 's/\.\././g'`"

    _min_major="`echo $_min | cut -d. -f1`"
    _min_minor="`echo $_min | cut -d. -f2`"
    _min_patch="`echo $_min | cut -d. -f3`"

    _cur_major="`echo $_cur | cut -d. -f1`"
    _cur_minor="`echo $_cur | cut -d. -f2`"
    _cur_patch="`echo $_cur | cut -d. -f3`"

    if [ "x$_min_major" = "x" ] ; then
        _min_major=0
    fi
    if [ "x$_min_minor" = "x" ] ; then
        _min_minor=0
    fi
    if [ "x$_min_patch" = "x" ] ; then
        _min_patch=0
    fi
    if [ "x$_cur_minor" = "x" ] ; then
        _cur_major=0
    fi
    if [ "x$_cur_minor" = "x" ] ; then
        _cur_minor=0
    fi
    if [ "x$_cur_patch" = "x" ] ; then
        _cur_patch=0
    fi

    # $VERBOSE_ECHO "Checking if ${_cur_major}.${_cur_minor}.${_cur_patch} is greater than ${_min_major}.${_min_minor}.${_min_patch}"

    RESULT=1
    if [ $_min_major -lt $_cur_major ] ; then
        RESULT=0
    elif [ $_min_major -eq $_cur_major ] ; then
        if [ $_min_minor -lt $_cur_minor ] ; then
            RESULT=0
        elif [ $_min_minor -eq $_cur_minor ] ; then
            if [ $_min_patch -lt $_cur_patch ] ; then
                RESULT=0
            elif [ $_min_patch -eq $_cur_patch ] ; then
                RESULT=0
            fi
        fi
    fi

    if [ $RESULT -eq 1 ] ; then
        echo "yes (version $1)"
    else
        echo "no (version $1)"
    fi

    return $RESULT
}

echo -n "checking for autoconf >= $AUTOCONF_REQUIRED_VERSION ... "
if autoconf --version >/dev/null; then
    VER=$(autoconf --version | grep -iw autoconf | sed "s/.* \([0-9.]*\)[-a-z0-9]*$/\1/")
    check_version $VER $AUTOCONF_REQUIRED_VERSION
else
    echo "not found"
    exit 1
fi

echo -n "checking for automake >= $AUTOMAKE_REQUIRED_VERSION ... "
if automake --version >/dev/null; then
    VER=$(automake --version | grep -iw automake | sed "s/.* \([0-9.]*\)[-a-z0-9]*$/\1/")
    check_version $VER $AUTOMAKE_REQUIRED_VERSION
else
    echo "not found"
    exit 1
fi

aclocal
autoheader
automake --add-missing
autoconf
