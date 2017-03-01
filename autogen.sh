#!/bin/sh
#
#  Copyright (C) 2002  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# Run this to generate all the initial autoconf files, etc.
#
DIE=0
AUTOCONF="autoconf"
AUTOHEADER=""

# Check for autoconf
(${AUTOCONF} --version) < /dev/null > /dev/null 2>&1 || {
	echo
        echo "You must have ${AUTOCONF} installed to compile from CVS."
        echo "Download the appropriate package for your distribution,"
        echo "or get the source tarball at ftp://ftp.gnu.org/pub/gnu/"
        DIE=1
}

if test "$DIE" -eq 1; then
        exit 1
fi

if test -n ${AUTOHEADER}; then
   echo "Running ${AUTOHEADER} to create a template configuration header file..."
   ${AUTOHEADER}
   if test $? != "0"; then
      echo "Running ${AUTOHEADER} failed, exiting..."
      exit 1
   fi
fi

echo ""
echo "Running ${AUTOCONF} to create 'configure'..."
${AUTOCONF}
if test $? != "0"; then
   echo "Running ${AUTOCONF} failed, exiting..."
   exit 1
fi


# Run confure to start off with a buildable system unless no-config is
# present on the command line.
if echo "$*" | grep -v "no-config" > /dev/null 2>&1; then
   if [ -x config.status -a -z "$*" ]; then
     ./config.status --recheck
   else
     if test -z "$*"; then
       echo ""
       echo "I am going to run ./configure with no arguments - if you wish "
       echo "to pass any to it, please specify them on the $0 command line."
       echo "If you do not wish to run ./configure, press Ctrl-C now."
       echo ""
       trap 'echo "configure aborted" ; exit 0' 1 2 15
       sleep 1
     fi
     ./configure "$@"
   fi
fi
