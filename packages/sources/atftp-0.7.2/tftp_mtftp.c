/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp_mtftp.c
 *    receive file from mtftp server
 *
 * $Id: tftp_mtftp.c,v 1.9 2004/01/24 05:00:59 jp Exp $
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

#ifdef HAVE_MTFTP

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <arpa/tftp.h>
#include <netdb.h>
#include <string.h>
#include <sys/stat.h>
#include "tftp.h"
#include "tftp_io.h"
#include "tftp_def.h"
#include "options.h"

#define S_LISTEN        0
#define S_OPEN          1
#define S_RECEIVE       2
#define S_SEND_REQ      3
#define S_SEND_ACK      4
#define S_WAIT_PACKET   5
#define S_DATA_RECEIVED 6
#define S_ABORT         7
#define S_END           8

#define LISTEN  100
#define OPEN    101
#define RECEIVE 102

#ifdef NB_OF_RETRY
#undef NB_OF_RETRY
#define NB_OF_RETRY 3
#else
#define NB_OF_RETRY 3
#endif

#define NB_BLOCK        (65536 / 32)

extern int tftp_cancel;

/* 
 * If mode = 0, count missed packet from block 0. Else, start after first
 * received block.
 */
int tftp_mtftp_missed_packet(unsigned int file_bitmap[], long last_block, int mode)
{
     int missed_block = 0;
     int block_number = 0;
     int first_block = -1;
     int i, j;

     if (mode == 0)
          first_block = 0;

     /* The first non zero bit is the first packet received. We start
        counting missed block there */
     for (i = 0; i < NB_BLOCK; i++)
     {
          for (j = 0; j < 32; j++)
          {
               if (first_block < 0)
               {
                    if (file_bitmap[i] & (1<<j))
                         first_block = block_number;
               }
               else
               {
                    if (!(file_bitmap[i] & (1<<j)))
                         missed_block++;
               }
               block_number++;
               if (last_block && (block_number == last_block))
                    return missed_block;
          }
     }
     return missed_block;
}


/*
 * Receive a file. This is implemented as a state machine using a while loop
 * and a switch statement. This follow pxe specification pages 32-34.
 */
int tftp_mtftp_receive_file(struct client_data *data)
{
     int state = S_SEND_REQ;    /* current state in the state machine */
     int timeout_state = state; /* what state should we go on when timeout */
     int result;
     long block_number = 0;
     long last_block_number = -1;/* block number of last block for multicast */
     int data_size;             /* size of data received */
     int sockfd = data->sockfd; /* just to simplify calls */
     int sock;
     struct sockaddr_storage sa; /* a copy of data.sa_peer */
     struct sockaddr_storage from;
     char from_str[SOCKADDR_PRINT_ADDR_LEN];
     struct tftphdr *tftphdr = (struct tftphdr *)data->data_buffer;
     FILE *fp = NULL;           /* the local file pointer */
     int number_of_timeout = 0;
     int timeout = 0;

     struct sockaddr_storage sa_mcast_group;
     int mcast_sockfd = 0;
     struct sockaddr_storage sa_mcast;
     union ip_mreq_storage mreq;
     struct addrinfo hints, *addrinfo;
     int err;

     int mode = LISTEN;
     unsigned int file_bitmap[NB_BLOCK];

     char string[MAXLEN];

     data->file_size = 0;
     tftp_cancel = 0;
     memset(&from, 0, sizeof(from));

     memset(&sa_mcast, 0, sizeof(struct sockaddr_storage));
     memset(&file_bitmap, 0, sizeof(file_bitmap));

     /* make sure the socket is not connected */
     sa.ss_family = AF_UNSPEC;
     connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));

     /* copy sa_peer structure */
     memcpy(&sa, &data->sa_peer, sizeof(sa));

     /* check to see if conversion is requiered */
     if (strcasecmp(data->tftp_options[OPT_MODE].value, "netascii") == 0)
          fprintf(stderr, "netascii convertion ignored\n");

     /* make sure the data buffer is SEGSIZE + 4 bytes */
     if (data->data_buffer_size != (SEGSIZE + 4))
     {
          data->data_buffer = realloc(data->data_buffer, SEGSIZE + 4);
          tftphdr = (struct tftphdr *)data->data_buffer;
          if (data->data_buffer == NULL)
          {
               fprintf(stderr, "atftp: memory allocation failure.\n");
               exit(1);
          }
          data->data_buffer_size = SEGSIZE + 4;
     }

     /* open the file for writing */
     if ((fp = fopen(data->local_file, "w")) == NULL)
     {
          fprintf(stderr, "atftp: can't open %s for writing.\n",
                  data->local_file);
          return ERR;
     }
     
     /* Configure multicast stuff,  look up the host */
     /* if valid, update s_inn structure */
     memset(&hints, 0, sizeof(hints));
     hints.ai_socktype = SOCK_DGRAM;
     if (!getaddrinfo(data->mtftp_mcast_ip, NULL, &hints, &addrinfo) &&
         !sockaddr_set_addrinfo(&sa_mcast_group, addrinfo))
     {
          freeaddrinfo(addrinfo);
          if (!sockaddr_is_multicast(&sa_mcast_group))
	  {
	       fprintf(stderr,
		       "mtftp: bad multicast address %s\n",
		       data->mtftp_mcast_ip);
	       exit(1);
	  }
     } 
     else
     {
	  fprintf(stderr, "atftp: bad multicast address %s",
		  data->mtftp_mcast_ip);
	  exit(1);
     }
     /* we need to open a new socket for multicast */
     if ((mcast_sockfd = socket(AF_INET, SOCK_DGRAM, 0))<0)
     {
	  perror("atftp: socket");
	  exit(1);
     }                   
     memset(&sa_mcast, 0, sizeof(sa_mcast));
     sa_mcast.ss_family = sa_mcast_group.ss_family;
     sockaddr_set_port(&sa, data->mtftp_client_port);
                         
     if (bind(mcast_sockfd, (struct sockaddr *)&sa_mcast,
	      sizeof(sa_mcast)) < 0)
     {
	  perror("atftp: bind");
	  exit(1);
     }
              
     sockaddr_get_mreq(&sa_mcast_group, &mreq);
     if (sa_mcast_group.ss_family == AF_INET)
          err = setsockopt(mcast_sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, 
                           &mreq.v4, sizeof(mreq.v4));
     else
          err = setsockopt(mcast_sockfd, IPPROTO_IPV6, IPV6_ADD_MEMBERSHIP,
                           &mreq.v6, sizeof(mreq.v6));
     if (err < 0)
     {
	  perror("atftp: setsockopt");
	  exit(1);
     }

     state = S_LISTEN;

     while (1)
     {
#ifdef DEBUG
          if (data->delay)
               usleep(data->delay*1000);
#endif
          if (tftp_cancel)
          {
               if (from.ss_family == 0)
                    state = S_ABORT;
               else
               {
                    if (mode == RECEIVE)
                    {
                         tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                         data->data_buffer_size);
                         if (data->trace)
                              fprintf(stderr,  "sent ERROR <code: %d, msg: %s>\n",
                                      EUNDEF, tftp_errmsg[EUNDEF]);
                    }
                    state = S_ABORT;
               }
               tftp_cancel = 0;
          }

          switch (state)
          {
	  case S_LISTEN:
               if (data->trace)
                    fprintf(stderr, "mtftp: listening for ongoing transfer on %s port %d\n",
                            data->mtftp_mcast_ip, data->mtftp_client_port);
               number_of_timeout = 0;
               mode = LISTEN;
               if (last_block_number > 0)
               {
                    timeout = data->mtftp_listen_delay - 
                         tftp_mtftp_missed_packet(file_bitmap, last_block_number, 1);
                    if (timeout < 0)
                         timeout = 0;
               }
               else
                    timeout = data->mtftp_listen_delay;
	       state = S_WAIT_PACKET;
	       timeout_state = S_OPEN;
	       break;
	  case S_OPEN:
               if (data->trace)
                    fprintf(stderr, "mtftp: opening new connection\n");
               mode = OPEN;
               block_number = 0;
               timeout = data->mtftp_timeout_delay;
	       state = S_SEND_REQ;
	       break;
          case S_RECEIVE:
               if (data->trace)
                    fprintf(stderr, "mtftp: connected, receiving\n");
               mode = RECEIVE;
               timeout = data->mtftp_timeout_delay;
	       state = S_SEND_ACK;
               break;
          case S_SEND_REQ:
               timeout_state = S_SEND_REQ;
               if (data->trace)
               {
                    opt_options_to_string(data->tftp_options, string, MAXLEN);
                    fprintf(stderr, "sent RRQ <file: %s, mode: %s <%s>>\n",
                            data->tftp_options[OPT_FILENAME].value,
                            data->tftp_options[OPT_MODE].value,
                            string);
               }
               /* send request packet */
               if (tftp_send_request(sockfd, &sa, RRQ, data->data_buffer,
                                     data->data_buffer_size,
                                     data->tftp_options) == ERR)
                    state = S_ABORT;
               else
                    state = S_WAIT_PACKET;

               sockaddr_set_port(&sa, 0); /* must be set to 0 before the fist call to
                                   tftp_get_packet, but it was set before the
                                   call to tftp_send_request with the server port */
               break;
          case S_SEND_ACK:
               timeout_state = S_SEND_ACK;
               
               /* walk the bitmap to find the next missing block */
               //prev_bitmap_hole =
               //tftp_find_bitmap_hole(prev_bitmap_hole, file_bitmap);
               //block_number = prev_bitmap_hole;

               if (data->trace)
                    fprintf(stderr, "sent ACK <block: %ld>\n", block_number);
               tftp_send_ack(sockfd, &sa, block_number);
               /* if we just ACK the last block we are done */
               if (block_number == last_block_number)
                    state = S_END;
               else
                    state = S_WAIT_PACKET;
               break;
          case S_WAIT_PACKET:
               data_size = data->data_buffer_size;
               /* receive the data */
               result = tftp_get_packet(sockfd, mcast_sockfd, &sock, &sa, &from,
					NULL, timeout, &data_size,
					data->data_buffer);
               switch (result)
               {
               case GET_TIMEOUT:
                    number_of_timeout++;
                    if (mode == LISTEN)
                    {
                         fprintf(stderr, "mtftp: timeout while listening\n");
                         state = S_OPEN;
                    }
                    else
                    {
                         fprintf(stderr, "mtftp: timeout: retrying...\n");
                         if (number_of_timeout > NB_OF_RETRY)
                              state = S_ABORT;
                         else
                              state = timeout_state;
                    }
                    break;
               case GET_ERROR:
                    if (mode == LISTEN)
                    {
                         fprintf(stderr,
                                 "mtftp: unexpected error received from server, ignoring\n");
                         break;
                    }
                    /* Can only receive this error from unicast */
                    if (!sockaddr_equal_addr(&sa, &from))
                    {
                         fprintf(stderr, "mtftp: error packet discarded from <%s>.\n",
                                 sockaddr_print_addr(&from, from_str, sizeof(from_str)));
                         break;
                    }
                    /* packet is for us */
                    fprintf(stderr, "mtftp: error received from server");
                    fwrite(tftphdr->th_msg, 1, data_size - 4 - 1, stderr);
                    fprintf(stderr, ">\n");
                    state = S_ABORT;
                    break;
               case GET_DATA:
                    /* Specification state that server source IP must matches, but
                       port is not a requierement (anyway we may not know the source
                       port yet) */
                    if (sockaddr_equal_addr(&sa, &from))
                    {
                         if (mode != LISTEN)
                         {
                              if (sock == sockfd)
                              {
                                   /* This is a unicast packet from the server. This should
                                      happend for the first data block only, when current
                                      block number is 0 and when in OPEN mode */
                                   if ((block_number > 0) || (mode != OPEN))
                                        fprintf(stderr,
                                                "mtftp: unexpected unicast packet from <%s>,"
                                                " continuing\n",
                                                sockaddr_print_addr(&from, from_str, sizeof(from_str)));
                                   else
                                        mode = RECEIVE;
                              }
                              else
                              {
                                   /* We receive data on the multicast socket, it should
                                      happend for packets 1 and above */
                                   if (block_number == 0)
                                   {
                                        mode = LISTEN;
                                        fprintf(stderr, "mtftp: got multicast data packet,"
                                                " falling back to listen mode\n");
                                   }
                              }
                         }
                         else
                         {
                              /* We are in listenning mode, we expect data on multicast
                                 socket only */
                              if (sock == sockfd)
                              {
                                   fprintf(stderr,
                                           "mtftp: unexpected unicast packet from <%s>.\n",
                                           sockaddr_print_addr(&from, from_str, sizeof(from_str)));
                                   break;
                              }
                         }
                    }
                    else
                    {
                         fprintf(stderr, "mtftp: unexpected packet from <%s>\n",
                                 sockaddr_print_addr(&from, from_str, sizeof(from_str)));
                         break;
                    }
                    number_of_timeout = 0;
                    state = S_DATA_RECEIVED;
                    break;
               case GET_DISCARD:
                    /* consider discarded packet as timeout to make sure when don't lock up
                       when doing multicast transfer and routing is broken or when using wrong
                       mcast IP or port */
                    number_of_timeout++;
                    fprintf(stderr, "mtftp: packet discard <%s>.\n",
                            sockaddr_print_addr(&from, from_str, sizeof(from_str)));
                    if (number_of_timeout > NB_OF_RETRY)
                         state = S_ABORT;
                    break;
               case ERR:
                    fprintf(stderr, "mtftp: unknown error.\n");
                    state = S_ABORT;
                    break;
               default:
                    fprintf(stderr, "mtftp: abnormal return value %d.\n",
                            result);
               }
               break;
          case S_DATA_RECEIVED:
               block_number = ntohs(tftphdr->th_block);
               if (data->trace)
                    fprintf(stderr, "received DATA <block: %ld, size: %d>\n",
                            block_number, data_size - 4);
               fseek(fp, (block_number - 1) * (data->data_buffer_size - 4),
                     SEEK_SET);
               if ((int)fwrite(tftphdr->th_data, 1, data_size - 4, fp) !=
                   (data_size - 4))
               {
                    
                    fprintf(stderr, "mtftp: error writing to file %s\n",
                            data->local_file);
		    if (mode == RECEIVE)
			 tftp_send_error(sockfd, &sa, ENOSPACE, data->data_buffer,
                                         data->data_buffer_size);
                    state = S_END;
                    break;
               }
               data->file_size += data_size; /* FIXME: not usefull */
               /* Record the block number of the last block. The last block
                  is the one with less data than the transfer block size */
               if (data_size < data->data_buffer_size)
                    last_block_number = block_number;
	       /* Mark the received block in the bitmap */
	       file_bitmap[(block_number - 1)/32]
		    |= (1 << ((block_number - 1) % 32));
	       /* if we are the master client we ack, else
		  we just wait for data */
	       if (mode == LISTEN)
               {
                    /* If we've not received all packets, continue listen. In the
                       case we've not seen the last packet yet, no choice but continuing
                       listen phase and eventually fall back to the open mode and download
                       the whole file again. If we've seen the last packet, we also continue
                       listen, but if we've got all the file we are done */
                    if (last_block_number < 0)
                         state = S_WAIT_PACKET;
                    else
                    {
                         if (tftp_mtftp_missed_packet(file_bitmap, last_block_number, 0))
                              state = S_WAIT_PACKET;
                         else
                         {
                              fprintf(stderr, "mtftp: got all packets\n");
                              state = S_END;
                         }
                    }
               }
               else
		    state = S_SEND_ACK;
               break;	       
	  case S_END:
	  case S_ABORT:
               /* close file */
               if (fp)
                    fclose(fp);
               /* drop multicast membership */
               if (sa_mcast_group.ss_family == AF_INET)
                    err = setsockopt(mcast_sockfd, IPPROTO_IP,
                                     IP_DROP_MEMBERSHIP, 
                                     &mreq.v4, sizeof(mreq.v4));
               else
                    err = setsockopt(mcast_sockfd, IPPROTO_IPV6,
                                     IPV6_DROP_MEMBERSHIP,
                                     &mreq.v6, sizeof(mreq.v6));
               if (err < 0)
               {
                    perror("setsockopt");
                    exit(1);
               }
               /* close socket */
               if (mcast_sockfd)
                    close(mcast_sockfd);
               /* return proper error code */
               if (state == S_END)
                    return OK;
               else
                    fprintf(stderr, "mtftp: aborting\n");
          default:
               return ERR;
          }
     }
}

#endif
     
