/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp_file.c
 *    client side file operations. File receiving and sending.
 *
 * $Id: tftp_file.c,v 1.42 2004/02/13 03:16:09 jp Exp $
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

#define S_BEGIN         0
#define S_SEND_REQ      1
#define S_SEND_ACK      2
#define S_SEND_OACK     3
#define S_SEND_DATA     4
#define S_WAIT_PACKET   5
#define S_REQ_RECEIVED  6
#define S_ACK_RECEIVED  7
#define S_OACK_RECEIVED 8
#define S_DATA_RECEIVED 9
#define S_ABORT         10
#define S_END           11

#define NB_BLOCK        2048

extern int tftp_cancel;

/*
 * Find a hole in the file bitmap.
 */
int tftp_find_bitmap_hole(int prev_hole, unsigned int *bitmap)
{
     int next_hole, next_word_no, next_bit_no;
     unsigned int next_word;

     /* initial stuff */
     next_hole = 0; /*prev_hole + 1;*/
     next_word_no = next_hole / 32;
     next_bit_no  = next_hole % 32;
     next_word = bitmap[next_word_no];

     /* Check if there is a remainder of the current word to traverse */
     if (next_bit_no != 0)
     {
          /* traverse remainder of word. We know that all previous
             bits are set */
          if (next_word == 0xffffffff)
          {
               next_bit_no = 0;
               next_word_no++;
               next_word = bitmap[next_word_no];
          }
     }

     /* travserse whole words */
     while ((next_word == 0xffffffff) && (next_word_no < NB_BLOCK))
     {
          next_word_no++;
          next_word = bitmap[next_word_no];
     }

     /* find the bit */
     next_word >>= next_bit_no;
     while (next_word & 1)
     {
         next_bit_no++;
         next_word >>= 1;
     }
     return (next_word_no * 32) + next_bit_no;
}


/*
 * Receive a file. This is implemented as a state machine using a while loop
 * and a switch statement. Function flow is as follow:
 *  - sanity check
 *  - enter state machine
 *
 *     1) send request
 *     2) wait reply
 *          - if DATA packet, read it, send an acknoledge, goto 2
 *          - if OACK (option acknowledge) acknowledge this option, goto 2
 *          - if ERROR abort
 *          - if TIMEOUT goto previous state
 */
int tftp_receive_file(struct client_data *data)
{
     int state = S_SEND_REQ;    /* current state in the state machine */
     int timeout_state = state; /* what state should we go on when timeout */
     int result;
     long block_number = 0;
     long last_block_number = -1;/* block number of last block for multicast */
     int data_size;             /* size of data received */
     int sockfd = data->sockfd; /* just to simplify calls */
     struct sockaddr_storage sa; /* a copy of data.sa_peer */
     struct sockaddr_storage from;
     char from_str[SOCKADDR_PRINT_ADDR_LEN];
     int connected;             /* 1 when sockfd is connected */
     struct tftphdr *tftphdr = (struct tftphdr *)data->data_buffer;
     FILE *fp = NULL;           /* the local file pointer */
     int number_of_timeout = 0;
     int convert = 0;           /* if true, do netascii convertion */

     int oacks = 0;             /* count OACK for improved error checking */
     int multicast = 0;         /* set to 1 if multicast */
     int mc_port;               /* multicast port */
     char mc_addr[IPADDRLEN];   /* multicast address */
     int mcast_sockfd = 0;
     struct addrinfo hints, *addrinfo;
     struct sockaddr_storage sa_mcast_group;
     struct sockaddr_storage sa_mcast;
     union ip_mreq_storage mreq;
     int master_client = 0;
     unsigned int file_bitmap[NB_BLOCK];
     int prev_bitmap_hole = -1; /* the previous hole found in the bitmap */
     char string[MAXLEN];

     long prev_block_number = 0; /* needed to support netascii convertion */
     int temp = 0;
     int err;

     data->file_size = 0;
     tftp_cancel = 0;

     memset(&from, 0, sizeof(from));
     memset(&sa_mcast_group, 0, sizeof(sa_mcast_group));
     memset(&file_bitmap, 0, sizeof(file_bitmap));

     /* make sure the socket is not connected */
     sa.ss_family = AF_UNSPEC;
     connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
     connected = 0;

     /* copy sa_peer structure */
     memcpy(&sa, &data->sa_peer, sizeof(sa));

     /* check to see if conversion is requiered */
     if (strcasecmp(data->tftp_options[OPT_MODE].value, "netascii") == 0)
          convert = 1;

     /* make sure the data buffer is SEGSIZE + 4 bytes */
     if (data->data_buffer_size != (SEGSIZE + 4))
     {
          data->data_buffer = realloc(data->data_buffer, SEGSIZE + 4);
          tftphdr = (struct tftphdr *)data->data_buffer;
          if (data->data_buffer == NULL)
          {
               fprintf(stderr, "tftp: memory allocation failure.\n");
               exit(1);
          }
          data->data_buffer_size = SEGSIZE + 4;
     }

     /* open the file for writing */
     if ((fp = fopen(data->local_file, "w")) == NULL)
     {
          fprintf(stderr, "tftp: can't open %s for writing.\n",
                  data->local_file);
          return ERR;
     }

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
                    tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                    data->data_buffer_size);
                    if (data->trace)
                         fprintf(stderr,  "sent ERROR <code: %d, msg: %s>\n",
                                 EUNDEF, tftp_errmsg[EUNDEF]);
                    state = S_ABORT;
               }
               tftp_cancel = 0;
          }

          switch (state)
          {
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

               sockaddr_set_port(&sa, sockaddr_get_port(&data->sa_peer));
               /* send request packet */
               if (tftp_send_request(sockfd, &sa, RRQ, data->data_buffer,
                                     data->data_buffer_size,
                                     data->tftp_options) == ERR)
                    state = S_ABORT;
               else
                    state = S_WAIT_PACKET;
               sockaddr_set_port(&sa, 0); /* must be set to 0 before the fist call to
                                   tftp_get_packet, but is was set before the
                                   call to tftp_send_request */
               break;
          case S_SEND_ACK:
               timeout_state = S_SEND_ACK;
               if (multicast)
               {
                    /* walk the bitmap to find the next missing block */
                    prev_bitmap_hole =
                         tftp_find_bitmap_hole(prev_bitmap_hole, file_bitmap);
                    block_number = prev_bitmap_hole;
               }
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
               if (multicast)
               {
                    result = tftp_get_packet(sockfd, mcast_sockfd, NULL, &sa, &from,
                                             NULL, data->timeout, &data_size,
                                             data->data_buffer);
                    /* RFC2090 state we should verify source address as well
                       as source port */
                    if (!sockaddr_equal(&sa, &from))
                    {
                         result = GET_DISCARD;
                         fprintf(stderr, "source address or port mismatch\n");
                    }
               }
               else
               {
                    result = tftp_get_packet(sockfd, -1, NULL, &sa, &from, NULL,
                                             data->timeout, &data_size,
                                             data->data_buffer);
                    /* Check that source port match */
                    if ((sockaddr_get_port(&sa) != sockaddr_get_port(&from)) &&
                        ((result == GET_OACK) || (result == GET_ERROR) ||
                         (result == GET_DATA)))
                    {
                         if (data->checkport)
                         {
                              result = GET_DISCARD;
                              fprintf(stderr, "source port mismatch\n");
                         }
                         else
                              fprintf(stderr, "source port mismatch, check bypassed");
                    }
               }

               switch (result)
               {
               case GET_TIMEOUT:
                    number_of_timeout++;
                    fprintf(stderr, "timeout: retrying...\n");
                    if (number_of_timeout > NB_OF_RETRY)
                         state = S_ABORT;
                    else
                         state = timeout_state;
                    break;
               case GET_OACK:
                    number_of_timeout = 0;
                    /* if the socket if not connected, connect it */
                    if (!connected)
                    {
                         connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
                         connected = 1;
                    }
                    state = S_OACK_RECEIVED;
                    break;
               case GET_ERROR:
                    fprintf(stderr, "tftp: error received from server <");
                    fwrite(tftphdr->th_msg, 1, data_size - 4 - 1, stderr);
                    fprintf(stderr, ">\n");
                    state = S_ABORT;
                    break;
               case GET_DATA:
                    number_of_timeout = 0;
                    /* if the socket if not connected, connect it */
                    if (!connected)
                    {
                         connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
                         connected = 1;
                    }
                    state = S_DATA_RECEIVED;
                    break;
               case GET_DISCARD:
                    /* consider discarded packet as timeout to make sure when don't
                       lock up when doing multicast transfer and routing is broken */
                    number_of_timeout++;
                    fprintf(stderr, "tftp: packet discard <%s:%d>.\n",
                            sockaddr_print_addr(&from, from_str, sizeof(from_str)),
                            sockaddr_get_port(&from));
                    if (number_of_timeout > NB_OF_RETRY)
                         state = S_ABORT;
                    break;
               case ERR:
                    fprintf(stderr, "tftp: unknown error.\n");
                    state = S_ABORT;
                    break;
               default:
                    fprintf(stderr, "tftp: abnormal return value %d.\n",
                            result);
               }
               break;
          case S_OACK_RECEIVED:
               oacks++;
               if (multicast)
               {
                    /* This is not the first oack. From the RFC, I don't think
                       it is illegal to receive many OACK. Need to check more
                       into that, but server may send us an OACK with mc=0 anytime */

#if 0
                    /* If we are a master, it is abnormal to receive again
                     * an OACK. We should terminate the file transfer of we'll
                     * timeout and exit.
                     */
                    if (master_client == 1)
                    {
                         tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                         data->data_buffer_size);
                         fprintf(stderr, "tftp: unexpected OACK\n");
                         state = S_ABORT;
                         break;
                    }
#endif
                    /* parse OACK options */
                    opt_parse_options(data->data_buffer, data_size,
                                      data->tftp_options_reply);
                    if ((result = opt_get_multicast(data->tftp_options_reply,
                                                    mc_addr, &mc_port,
                                                    &master_client)) > -1)
                         if (master_client == 1)
                         {
                              if (data->trace)
                                   fprintf(stderr, "received OACK <mc = 1>\n");
                              state = S_SEND_ACK;
                         }
                         else
                         {
                              if (data->trace)
                                   fprintf(stderr, "received OACK <mc = 0>\n");
                              state = S_WAIT_PACKET;
                         }
                    else
                    {
                         tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                         data->data_buffer_size);
                         fprintf(stderr, "tftp: error parsing OACK\n");
                         state = S_ABORT;
                    }
                    break;
               }
               else
               {
                    /* Normally we shouldn't receive more than one OACK
                       in non-multicast mode. */
                    if (oacks > 1)
                    {
                         tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                         data->data_buffer_size);
                         fprintf(stderr, "tftp: unexpected OACK\n");
                         state = S_ABORT;
                         break;
                    }

                    /* clean the tftp_options structure */
                    memcpy(data->tftp_options_reply, tftp_default_options,
                           sizeof(tftp_default_options));
                    /*
                     * look in the returned string for tsize, timeout, blksize
                     * or multicast
                     */
                    opt_disable_options(data->tftp_options_reply, NULL);
                    opt_parse_options(data->data_buffer, data_size,
                                      data->tftp_options_reply);
                    if (data->trace)
                         fprintf(stderr, "received OACK <");
                    /* tsize: funny, now we know the file size */
                    if ((result = opt_get_tsize(data->tftp_options_reply)) >
                        -1)
                    {
                         if (data->trace)
                              fprintf(stderr, "tsize: %d, ", result);
                    }
                    /* timeout */
                    if ((result = opt_get_timeout(data->tftp_options_reply))
                        > -1)
                    {
                         if (data->trace)
                              fprintf(stderr, "timeout: %d, ", result);
                    }
                    /* blksize: resize the buffer please */
                    if ((result = opt_get_blksize(data->tftp_options_reply))
                        > -1)
                    {
                         if (data->trace)
                              fprintf(stderr, "blksize: %d, ", result);

                         data->data_buffer = realloc(data->data_buffer,
                                                     result + 4);
                         tftphdr = (struct tftphdr *)data->data_buffer;
                         if (data->data_buffer == NULL)
                         {
                              fprintf(stderr,
                                      "tftp: memory allocation failure.\n");
                              exit(1);
                         }
                         data->data_buffer_size = result + 4;
                    }
                    /* multicast: yish, it's more complex. If we are a master,
                       we are responsible to ask packet with an ACK. If we are
                       not master, then just receive packets. Missing packets
                       will be asked when we become a master client. Also we
                       can receive data in any order, with hole. The option
                       reply contain the new address and port to listen to.*/
                    if ((result = opt_get_multicast(data->tftp_options_reply,
                                                    mc_addr, &mc_port,
                                                    &master_client)) > -1)
                    {
                         if (data->trace)
                              fprintf(stderr, "multicast: %s,%d,%d, ", mc_addr,
                                      mc_port, master_client);
                         /* look up the host */
                         /* if valid, update s_inn structure */
                         memset(&hints, 0, sizeof(hints));
                         hints.ai_socktype = SOCK_DGRAM;
                         if (!getaddrinfo(mc_addr, NULL, &hints, &addrinfo) &&
                             !sockaddr_set_addrinfo(&sa_mcast_group, addrinfo))
                         {
                              if (!sockaddr_is_multicast(&sa_mcast_group))
                              {
                                   fprintf(stderr,
                                           "atftp: bad multicast address %s\n",
                                           mc_addr);
                                   exit(1);
                              }
                              freeaddrinfo(addrinfo);
                         }
                         else
                         {
                              fprintf(stderr, "tftp: bad multicast address %s",
                                      mc_addr);
                              exit(1);
                         }
                         /* we need to open a new socket for multicast */
                         if ((mcast_sockfd = socket(sa_mcast_group.ss_family,
                                                    SOCK_DGRAM, 0))<0)
			 {
			      fprintf(stderr,
				      "atftp: unable to open socket\n");
                              exit(1);
			 }

                         memset(&sa_mcast, 0, sizeof(sa_mcast));
                         sa_mcast.ss_family = sa_mcast_group.ss_family;
                         sockaddr_set_port(&sa_mcast, mc_port);

                         if (bind(mcast_sockfd, (struct sockaddr *)&sa_mcast,
                                  sizeof(sa_mcast)) < 0)
                         {
                              perror("bind"); /* FIXME */
                              exit(1);
                         }

                         sockaddr_get_mreq(&sa_mcast_group, &mreq);
                         if (sa_mcast_group.ss_family == AF_INET)
                              err = setsockopt(mcast_sockfd, IPPROTO_IP,
                                               IP_ADD_MEMBERSHIP,
                                               &mreq.v4, sizeof(mreq.v4));
                         else
                              err = setsockopt(mcast_sockfd, IPPROTO_IPV6,
                                               IPV6_ADD_MEMBERSHIP,
                                               &mreq.v6, sizeof(mreq.v6));
                         if (err < 0)
                         {
                              perror("setsockopt");
                              exit(1);
                         }
                         multicast = 1;
                    }
               }
               if (data->trace)
                    fprintf(stderr, "\b\b>\n");
               if ((multicast && master_client) || (!multicast))
                    state = S_SEND_ACK;
               else
                    state = S_WAIT_PACKET;
               break;
          case S_DATA_RECEIVED:
               if ((multicast && master_client) || (!multicast))
                    timeout_state = S_SEND_ACK;
               else
                    timeout_state = S_WAIT_PACKET;

	       if (multicast)
		    block_number = ntohs(tftphdr->th_block);
	       else
	       {
		    block_number = tftp_rollover_blocknumber(
			ntohs(tftphdr->th_block), prev_block_number, 0);
	       }
               if (data->trace)
                    fprintf(stderr, "received DATA <block: %ld, size: %d>\n",
                            block_number, data_size - 4);

               if (tftp_file_write(fp, tftphdr->th_data, data->data_buffer_size - 4, block_number,
                                   data_size - 4, convert, &prev_block_number, &temp)
                   != data_size - 4)
               {

                    fprintf(stderr, "tftp: error writing to file %s\n",
                            data->local_file);
                    tftp_send_error(sockfd, &sa, ENOSPACE, data->data_buffer,
                                    data->data_buffer_size);
                    state = S_ABORT;
                    break;
               }
               data->file_size += data_size;
               /* Record the block number of the last block. The last block
                  is the one with less data than the transfer block size */
               if (data_size < data->data_buffer_size)
                    last_block_number = block_number;
               if (multicast)
               {
                    /* Mark the received block in the bitmap */
                    file_bitmap[(block_number - 1)/32]
                         |= (1 << ((block_number - 1) % 32));
                    /* if we are the master client we ack, else
                       we just wait for data */
                    if (master_client || !multicast)
                         state = S_SEND_ACK;
                    else
                         state = S_WAIT_PACKET;
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
               if (multicast)
               {
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
               }
               /* close multicast socket */
               if (mcast_sockfd)
                    close(mcast_sockfd);
               /* return proper error code */
               if (state == S_END)
                    return OK;
               else
                    fprintf(stderr, "tftp: aborting\n");
          default:
               return ERR;
          }
     }
}

/*
 * Send a file. This is implemented as a state machine using a while loop
 * and a switch statement. Function flow is as follow:
 *  - sanity check
 *  - enter state machine
 *
 *     1) send request
 *     2) wait replay
 *          - if ACK, goto 3
 *          - if OACK (option acknowledge) acknowledge this option, goto 2
 *          - if ERROR abort
 *          - if TIMEOUT goto previous state
 *     3) send data, goto 2
 */
int tftp_send_file(struct client_data *data)
{
     int state = S_SEND_REQ;    /* current state in the state machine */
     int timeout_state = state; /* what state should we go on when timeout */
     int result;
     long block_number = 0;
     long last_block = -1;
     int data_size;             /* size of data received */
     int sockfd = data->sockfd; /* just to simplify calls */
     struct sockaddr_storage sa; /* a copy of data.sa_peer */
     struct sockaddr_storage from;
     char from_str[SOCKADDR_PRINT_ADDR_LEN];
     int connected;             /* 1 when sockfd is connected */
     struct tftphdr *tftphdr = (struct tftphdr *)data->data_buffer;
     FILE *fp;                  /* the local file pointer */
     int number_of_timeout = 0;
     struct stat file_stat;
     int convert = 0;           /* if true, do netascii convertion */
     char string[MAXLEN];

     long prev_block_number = 0; /* needed to support netascii convertion */
     long prev_file_pos = 0;
     int temp = 0;

     data->file_size = 0;
     tftp_cancel = 0;
     memset(&from, 0, sizeof(from));

     /* make sure the socket is not connected */
     sa.ss_family = AF_UNSPEC;
     connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
     connected = 0;

     /* copy sa_peer structure */
     memcpy(&sa, &data->sa_peer, sizeof(sa));

     /* check to see if conversion is requiered */
     if (strcasecmp(data->tftp_options[OPT_MODE].value, "netascii") == 0)
          convert = 1;

     /* make sure the data buffer is SEGSIZE + 4 bytes */
     if (data->data_buffer_size != (SEGSIZE + 4))
     {
          data->data_buffer = realloc(data->data_buffer, SEGSIZE + 4);
          tftphdr = (struct tftphdr *)data->data_buffer;
          if (data->data_buffer == NULL)
          {
               fprintf(stderr, "tftp: memory allocation failure.\n");
               exit(1);
          }
          data->data_buffer_size = SEGSIZE + 4;
     }

     /* open the file for reading */
     if ((fp = fopen(data->local_file, "r")) == NULL)
     {
          fprintf(stderr, "tftp: can't open %s for reading.\n",
                  data->local_file);
          return ERR;
     }

     /* When sending a file with the tsize argument, we shall
        put the file size as argument */
     fstat(fileno(fp), &file_stat);
     if (opt_get_tsize(data->tftp_options) > -1)
          opt_set_tsize(file_stat.st_size, data->tftp_options);

     while (1)
     {
#ifdef DEBUG
          if (data->delay)
               usleep(data->delay*1000);
#endif
          if (tftp_cancel)
          {
               /* Make sure we know the peer's address */
               if (from.ss_family == 0)
                    state = S_ABORT;
               else
               {
                    tftp_send_error(sockfd, &sa, EUNDEF, data->data_buffer,
                                    data->data_buffer_size);
                    if (data->trace)
                         fprintf(stderr,  "sent ERROR <code: %d, msg: %s>\n",
                                 EUNDEF, tftp_errmsg[EUNDEF]);
                    state = S_ABORT;
               }
               tftp_cancel = 0;
          }

          switch (state)
          {
          case S_SEND_REQ:
               timeout_state = S_SEND_REQ;
               if (data->trace)
               {
                    opt_options_to_string(data->tftp_options, string, MAXLEN);
                    fprintf(stderr, "sent WRQ <file: %s, mode: %s <%s>>\n",
                            data->tftp_options[OPT_FILENAME].value,
                            data->tftp_options[OPT_MODE].value,
                            string);
               }

               sockaddr_set_port(&sa, sockaddr_get_port(&data->sa_peer));
               /* send request packet */
               if (tftp_send_request(sockfd, &sa, WRQ, data->data_buffer,
                                     data->data_buffer_size,
                                     data->tftp_options) == ERR)
                    state = S_ABORT;
               else
                    state = S_WAIT_PACKET;
               sockaddr_set_port(&sa, 0); /* must be set to 0 before the fist call to
                                   tftp_get_packet, but is was set before the
                                   call to tftp_send_request */
               break;
          case S_SEND_DATA:
               timeout_state = S_SEND_DATA;

               data_size = tftp_file_read(fp, tftphdr->th_data, data->data_buffer_size - 4, block_number,
                                          convert, &prev_block_number, &prev_file_pos, &temp);
               data_size += 4;  /* need to consider tftp header */

               if (feof(fp))
                    last_block = block_number;
               tftp_send_data(sockfd, &sa, block_number + 1,
                              data_size, data->data_buffer);
               data->file_size += data_size;
               if (data->trace)
                    fprintf(stderr, "sent DATA <block: %ld, size: %d>\n",
                            block_number + 1, data_size - 4);
               state = S_WAIT_PACKET;
               break;
          case S_WAIT_PACKET:
               data_size = data->data_buffer_size;
               result = tftp_get_packet(sockfd, -1, NULL, &sa, &from, NULL,
                                        data->timeout, &data_size,
                                        data->data_buffer);
               /* check that source port match */
               if (sockaddr_get_port(&sa) != sockaddr_get_port(&from))
               {
                    if ((data->checkport) &&
                        ((result == GET_ACK) || (result == GET_OACK) ||
                         (result == GET_ERROR)))
                         result = GET_DISCARD;
                    else
                         fprintf(stderr, "source port mismatch, check bypassed");
               }

               switch (result)
               {
               case GET_TIMEOUT:
                    number_of_timeout++;
                    fprintf(stderr, "timeout: retrying...\n");
                    if (number_of_timeout > NB_OF_RETRY)
                         state = S_ABORT;
                    else
                         state = timeout_state;
                    break;
               case GET_ACK:
                    number_of_timeout = 0;
                    /* if the socket if not connected, connect it */
                    if (!connected)
                    {
                         //connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
                         connected = 1;
                    }
		    block_number = tftp_rollover_blocknumber(
			ntohs(tftphdr->th_block), prev_block_number, 0);
                    if (data->trace)
                         fprintf(stderr, "received ACK <block: %ld>\n",
                                 block_number);
                    if ((last_block != -1) && (block_number > last_block))
                    {
                         state = S_END;
                         break;
                    }
                    state = S_SEND_DATA;
                    break;
               case GET_OACK:
                    number_of_timeout = 0;
                    /* if the socket if not connected, connect it */
                    if (!connected)
                    {
                         //connect(sockfd, (struct sockaddr *)&sa, sizeof(sa));
                         connected = 1;
                    }
                    state = S_OACK_RECEIVED;
                    break;
               case GET_ERROR:
                    fprintf(stderr, "tftp: error received from server <");
                    fwrite(tftphdr->th_msg, 1, data_size - 4 - 1, stderr);
                    fprintf(stderr, ">\n");
                    state = S_ABORT;
                    break;
               case GET_DISCARD:
                    /* consider discarded packet as timeout to make sure when don't lock up
                       if routing is broken */
                    number_of_timeout++;
                    fprintf(stderr, "tftp: packet discard <%s:%d>.\n",
                            sockaddr_print_addr(&from, from_str, sizeof(from_str)),
                            sockaddr_get_port(&from));
                    if (number_of_timeout > NB_OF_RETRY)
                         state = S_ABORT;
                    break;
               case ERR:
                    fprintf(stderr, "tftp: unknown error.\n");
                    state = S_ABORT;
                    break;
               default:
                    fprintf(stderr, "tftp: abnormal return value %d.\n",
                            result);
               }
               break;
          case S_OACK_RECEIVED:
               /* clean the tftp_options structure */
               memcpy(data->tftp_options_reply, tftp_default_options,
                      sizeof(tftp_default_options));
               /*
                * look in the returned string for tsize, timeout, blksize or
                * multicast
                */
               opt_disable_options(data->tftp_options_reply, NULL);
               opt_parse_options(data->data_buffer, data_size,
                                 data->tftp_options_reply);
               if (data->trace)
                    fprintf(stderr, "received OACK <");
               /* tsize: funny, now we know the file size */
               if ((result = opt_get_tsize(data->tftp_options_reply)) > -1)
               {
                    if (data->trace)
                         fprintf(stderr, "tsize: %d, ", result);
               }
               /* timeout */
               if ((result = opt_get_timeout(data->tftp_options_reply)) > -1)
               {
                    if (data->trace)
                         fprintf(stderr, "timeout: %d, ", result);
               }
               /* blksize: resize the buffer please */
               if ((result = opt_get_blksize(data->tftp_options_reply)) > -1)
               {
                    if (data->trace)
                         fprintf(stderr, "blksize: %d, ", result);
                    data->data_buffer = realloc(data->data_buffer,
                                                result + 4);
                    tftphdr = (struct tftphdr *)data->data_buffer;
                    if (data->data_buffer == NULL)
                    {
                        fprintf(stderr,
                                "tftp: memory allocation failure.\n");
                        exit(1);
                    }
                    data->data_buffer_size = result + 4;
               }
               /* multicast: yish, it's more complex. If we are a master,
                  we are responsible to ask packet with an ACK. If we are
                  not master, then just receive packets. Missing packets
                  will be asked when we become a master client */

               if (data->trace)
                    fprintf(stderr, "\b\b>\n");
               state = S_SEND_DATA;
               break;
          case S_END:
               if (fp)
                    fclose(fp);
               return OK;
               break;
          case S_ABORT:
               if (fp)
                    fclose(fp);
               fprintf(stderr, "tftp: aborting\n");
          default:
               return ERR;
          }
     }
}
