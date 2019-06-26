/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp_def.c
 *
 * $Id: tftp_def.c,v 1.15 2004/02/13 03:16:09 jp Exp $
 *
 * Copyright (c) 2000 Jean-Pierre Lefebvre <helix@step.polymtl.ca>
 *                and Remi Lefebvre <remi@debian.org>
 *
 * atftp is free software; you can redistribute them and/or modify them
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 */

#include "config.h"

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <arpa/inet.h>
#include "tftp_def.h"
#include "options.h"
#include "logger.h"

/*
 * This is the default option structure, that must be used
 * for initialisation.
 */

// FIXME: is there a way to use TIMEOUT and SEGSIZE here?
struct tftp_opt tftp_default_options[OPT_NUMBER + 1] = {
     { "filename", "", 0, 1},   /* file to transfer */
     { "mode", "octet", 0, 1},  /* mode for transfer */
     { "tsize", "0", 0, 1 },    /* RFC1350 options. See RFC2347, */
     { "timeout", "5", 0, 1 },  /* 2348, 2349, 2090.  */
     { "blksize", "512", 0, 1 }, /* This is the default option */
     { "multicast", "", 0, 1 }, /* structure */
     { "password", "", 0, 1},   /* password */
     { "", "", 0, 0}
};

/* Error message defined in RFC1350. */
char *tftp_errmsg[9] = {
     "Undefined error code",
     "File not found",
     "Access violation",
     "Disk full or allocation exceeded",
     "Illegal TFTP operation",
     "Unknown transfer ID",
     "File already exists",
     "No such user",
     "Failure to negotiate RFC1782 options",
};


/*
 * Compute the difference of two timeval structs handling wrap around.
 * The result is returned in *res.
 * Return value are:
 *     1 if t1 > t0
 *     0 if t1 = t0
 *    -1 if t1 < t0
 */ 
int timeval_diff(struct timeval *res, struct timeval *t1, struct timeval *t0)
{
     int neg = 1;
     res->tv_sec = t1->tv_sec - t0->tv_sec;
     res->tv_usec = t1->tv_usec - t0->tv_usec;
     
     while (res->tv_sec < 0 || res->tv_usec < 0)
     {
	  if (res->tv_sec < 0 || (res->tv_sec == 0 && res->tv_usec < 0))
	  {
	      neg = -neg;
	      res->tv_sec = -res->tv_sec;
	      res->tv_usec = -res->tv_usec;
	  }
	  if (res->tv_usec < 0)
	  {
	      long s = (res->tv_usec - 999999) / 1000000;
	      res->tv_sec += s;
	      res->tv_usec -= s * 1000000;
	  }
      }
      if (res->tv_usec >= 1000000)
      {
	  long s = res->tv_usec / 1000000;
	  res->tv_sec += s;
	  res->tv_usec -= s * 1000000;
      }
      if (res->tv_sec == 0 && res->tv_usec == 0)
      {
	  return 0;
      }
      return neg;
}

/*
 * Print a string in engineering notation.
 *
 * IN:
 *  value: value to print
 *  string: if NULL, the function print to stdout, else if print
 *          to the string.
 *  format: format string for printf.
 */
int print_eng(double value, char *string, int size, char *format)
{
     char suffix[] = {'f', 'p', 'n', 'u', 'm', 0, 'k', 'M', 'G', 'T', 'P'};
     double tmp;
     double div = 1e-15;
     int i;


     for (i = 0; i < 11; i++)
     {
          tmp = value / div;
          if ((tmp > 1.0) && (tmp < 1000.0))
               break;
          div *= 1000.0;
     }
     if (string)
          snprintf(string, size, format, tmp, suffix[i]);
     else
          printf(format, tmp, suffix[i]);
     return OK;
}

/*
 * This is a strncpy function that take care of string NULL termination
 */
inline char *Strncpy(char *to, const char *from, size_t size)
{
     strncpy(to, from, size);
     if (size>0) 
          to[size-1] = '\000';
     return to;
}


/* 
 * gethostbyname replacement that is reentrant. This function is copyied
 * from the libc manual.
 */
int Gethostbyname(char *addr, struct hostent *host)
{
     struct hostent *hp;
     char *tmpbuf;
     size_t tmpbuflen;
     int res;
     int herr;
     
     tmpbuflen = 1024;

     if ((tmpbuf = (char *)malloc(tmpbuflen)) == NULL)
          return ERR;

     res = gethostbyname_r(addr, host, tmpbuf, tmpbuflen, &hp, &herr);

     free(tmpbuf);

     /*  Check for errors. */
     if (res != 0)
     {
          logger(LOG_ERR, "%s: %d: gethostbyname_r: %s",
                 __FILE__, __LINE__, strerror(herr));
          return ERR;
     }
     if (hp != host)
     {
          logger(LOG_ERR, "%s: %d: abnormal return value",
                 __FILE__, __LINE__);
          return ERR;
     }

     return OK;
}

char *
sockaddr_print_addr(const struct sockaddr_storage *ss, char *buf, size_t len)
{
     const void *addr;
     if (ss->ss_family == AF_INET)
          addr = &((const struct sockaddr_in *)ss)->sin_addr;
     else if (ss->ss_family == AF_INET6)
          addr = &((const struct sockaddr_in6 *)ss)->sin6_addr;
     else
          assert(!"sockaddr_print: unsupported address family");
     return (char *)inet_ntop(ss->ss_family, addr, buf, len);
}

uint16_t sockaddr_get_port(const struct sockaddr_storage *ss)
{
     if (ss->ss_family == AF_INET)
          return ntohs(((const struct sockaddr_in *)ss)->sin_port);
     if (ss->ss_family == AF_INET6)
          return ntohs(((const struct sockaddr_in6 *)ss)->sin6_port);
     return 0;
}

void sockaddr_set_port(struct sockaddr_storage *ss, uint16_t port)
{
     if (ss->ss_family == AF_INET)
          ((struct sockaddr_in *)ss)->sin_port = htons(port);
     else if (ss->ss_family == AF_INET6)
          ((struct sockaddr_in6 *)ss)->sin6_port = htons(port);
     else
          assert(!"sockaddr_set_port: unsupported address family");
}

int sockaddr_equal(const struct sockaddr_storage *left,
                   const struct sockaddr_storage *right)
{
     if (left->ss_family != right->ss_family)
          return 0;
     if (left->ss_family == AF_INET)
     {
          const struct sockaddr_in
               *sa_left = (const struct sockaddr_in *)left,
               *sa_right = (const struct sockaddr_in *)right;
          return (sa_left->sin_port == sa_right->sin_port &&
                  sa_left->sin_addr.s_addr == sa_right->sin_addr.s_addr);
     }
     if (left->ss_family == AF_INET6)
     {
          const struct sockaddr_in6
               *sa_left = (const struct sockaddr_in6 *)left,
               *sa_right = (const struct sockaddr_in6 *)right;
          return (sa_left->sin6_port == sa_right->sin6_port &&
                  memcmp(&sa_left->sin6_addr, &sa_right->sin6_addr,
                         sizeof(sa_left->sin6_addr)) == 0 &&
                  sa_left->sin6_scope_id == sa_right->sin6_scope_id);
     }
     assert(!"sockaddr_equal: unsupported address family");
}

int sockaddr_equal_addr(const struct sockaddr_storage *left,
                        const struct sockaddr_storage *right)
{
     if (left->ss_family != right->ss_family)
          return 0;
     if (left->ss_family == AF_INET)
     {
          const struct sockaddr_in
               *sa_left = (const struct sockaddr_in *)left,
               *sa_right = (const struct sockaddr_in *)right;
          return sa_left->sin_addr.s_addr == sa_right->sin_addr.s_addr;
     }
     if (left->ss_family == AF_INET6)
     {
          const struct sockaddr_in6
               *sa_left = (const struct sockaddr_in6 *)left,
               *sa_right = (const struct sockaddr_in6 *)right;
          return (memcmp(&sa_left->sin6_addr, &sa_right->sin6_addr,
                         sizeof(sa_left->sin6_addr)) == 0 &&
                  sa_left->sin6_scope_id == sa_right->sin6_scope_id);
     }
     assert(!"sockaddr_equal_addr: unsupported address family");
}

int sockaddr_is_multicast(const struct sockaddr_storage *ss)
{
     if (ss->ss_family == AF_INET)
          return IN_MULTICAST(ntohl(((const struct sockaddr_in *)ss)
                                    ->sin_addr.s_addr));
     if (ss->ss_family == AF_INET6)
          return IN6_IS_ADDR_MULTICAST(&((const struct sockaddr_in6 *)ss)
                                       ->sin6_addr);
     return 0;
}

void sockaddr_get_mreq(const struct sockaddr_storage *ss,
                       union ip_mreq_storage *mreq)
{
     if (ss->ss_family == AF_INET)
     {
          const struct sockaddr_in *sa = (const struct sockaddr_in *)ss;
          mreq->v4.imr_multiaddr = sa->sin_addr;
          mreq->v4.imr_interface.s_addr = htonl(INADDR_ANY); 
     }
     else if (ss->ss_family == AF_INET6)
     {
          const struct sockaddr_in6 *sa = (const struct sockaddr_in6 *)ss;
          mreq->v6.ipv6mr_multiaddr = sa->sin6_addr;
          mreq->v6.ipv6mr_interface = 0; /* ??? */
     }
     else
     {
          assert(!"sockaddr_get_mreq: unsupported address family");
     }
}

int
sockaddr_set_addrinfo(struct sockaddr_storage *ss, const struct addrinfo *ai)
{
     while (ai->ai_family != AF_INET && ai->ai_family != AF_INET6)
     {
          ai = ai->ai_next;
          if (!ai)
          {
               errno = EAFNOSUPPORT;
               return -1;
          }
     }

     assert(sizeof(*ss) >= ai->ai_addrlen);
     memcpy(ss, ai->ai_addr, ai->ai_addrlen);
     return 0;
}
