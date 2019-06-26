/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp.h
 *
 * $Id: tftp.h,v 1.15 2003/03/19 04:02:49 jp Exp $
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

#ifndef tftp_h
#define tftp_h

#include <sys/time.h>
#include <sys/times.h>
#include "tftp_def.h"
#include "config.h"

struct client_data {
     char *data_buffer;         /* used for sending and receiving of data */
     int data_buffer_size;      /* size of the buffer, may be reallocated */

     char local_file[VAL_SIZE]; /* the file we are reading or writing is not
                                   necessary the same on the server */
     struct tftp_opt *tftp_options; /* hold requested options */
     struct tftp_opt *tftp_options_reply; /* hold server reply */

     int timeout;               /* client side timeout for select() */
     int checkport;             /* Disable TID check. Violate RFC */
     int trace;                 /* debugging information */
     int verbose;               /* to print message at each step */

     char hostname[MAXLEN];     /* peer's hostname */
     short port;                /* tftp port for the server, 69 by default */

     struct sockaddr_storage sa_peer; /* peer address and port */
     struct sockaddr_storage sa_local; /* local address and port */
     int sockfd;

     int connected;             /* we are 'connected' */

#ifdef HAVE_MTFTP
     /* for MTFTP */
     int mtftp_client_port;
     char mtftp_mcast_ip[MAXLEN];
     int mtftp_listen_delay;
     int mtftp_timeout_delay;
#endif

     /* statistics */
     struct timeval start_time;
     struct timeval end_time;
     int file_size;

#if DEBUG
     int delay;
#endif

};

/* Defined in tftp_file.c */
int tftp_find_bitmap_hole(int prev_hole, unsigned int *bitmap);
int tftp_receive_file(struct client_data *data);
int tftp_send_file(struct client_data *data);
/* Defined in tftp_mtftp.c */
#ifdef HAVE_MTFTP
int tftp_mtftp_receive_file(struct client_data *data);
#endif

#endif
