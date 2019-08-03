/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp_io.c
 *    I/O operation routines common to both client and server
 *
 * $Id: tftp_io.c,v 1.24 2004/02/19 01:30:00 jp Exp $
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
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <arpa/tftp.h>
#include <errno.h>
#include "string.h"
#include "tftp_io.h"
#include "logger.h"

/*
 *  2 bytes   string    1 byte  string  1 byte  string 1 byte  string
 * --------------------------------------------------------------------->
 *| Opcode  | Filename |   0   | Mode  |   0   | Opt1 |   0   | Value1 <
 * --------------------------------------------------------------------->
 *
 *    string  1 byte  string  1 byte
 *  >--------------------------------
 * <  OptN  |   0   | ValueN |   0   |
 *  >--------------------------------
 */
int tftp_send_request(int socket, struct sockaddr_storage *sa, short type,
                      char *data_buffer, int data_buffer_size,
                      struct tftp_opt *tftp_options)
{
     int i;
     int result;
     int buf_index = 0;
     struct tftphdr *tftphdr = (struct tftphdr *)data_buffer;
     char *filename = tftp_options[OPT_FILENAME].value;
     char *mode = tftp_options[OPT_MODE].value;

     /* write the opcode */
     tftphdr->th_opcode = htons(type);
     buf_index += 2;
     /* write file name */
     Strncpy(data_buffer + buf_index, filename, data_buffer_size - buf_index);
     buf_index += strlen(filename);
     buf_index++;
     Strncpy(data_buffer + buf_index, mode, data_buffer_size - buf_index);
     buf_index += strlen(mode);
     buf_index++;
     
     for (i = 2; ; i++)
     {
          if (strlen(tftp_options[i].option) == 0)
               break;
          if (tftp_options[i].enabled && tftp_options[i].specified)
          {
               if (i != OPT_PASSWORD)
               {
                   Strncpy(data_buffer + buf_index, tftp_options[i].option,
                           data_buffer_size - buf_index);
                   buf_index += strlen(tftp_options[i].option);
                   buf_index++;    
               }
               Strncpy(data_buffer + buf_index, tftp_options[i].value,
                       data_buffer_size - buf_index);
               buf_index += strlen(tftp_options[i].value);
               buf_index++;    
          }
     }
     /* send the buffer */
     result = sendto(socket, data_buffer, buf_index, 0,
                     (struct sockaddr *)sa, sizeof(*sa));
     if (result < 0)
          return ERR;
     return OK;
}

/*
 *  2 bytes   2 bytes
 * -------------------
 *| Opcode  | Block # |
 * -------------------
 */
int tftp_send_ack(int socket, struct sockaddr_storage *sa, long block_number)
{
     struct tftphdr tftphdr;
     int result;

     tftphdr.th_opcode = htons(ACK);
     tftphdr.th_block = htons((short)block_number);

     result = sendto(socket, &tftphdr, 4, 0, (struct sockaddr *)sa,
                     sizeof(*sa));
     if (result < 0)
          return ERR;
     return OK;
}

/*
 *  2 bytes   string  1 byte  string  1 byte  string  1 byte   string  1 byte
 * ---------------------------------------------------------------------------
 *| Opcode  | Opt1  |   0   | Value1 |   0   | OptN  |   0   | ValueN |   0   |
 * ---------------------------------------------------------------------------
 */
int tftp_send_oack(int socket, struct sockaddr_storage *sa, struct tftp_opt *tftp_options,
                   char *buffer, int buffer_size)
{
     
     int i;
     int result;
     int index = 0;
     struct tftphdr *tftphdr = (struct tftphdr *)buffer;

     /* write the opcode */
     tftphdr->th_opcode = htons(OACK);
     index += 2;
     
     for (i = 2; i < OPT_NUMBER; i++)
     {
          if (tftp_options[i].enabled && tftp_options[i].specified)
          {
               Strncpy(buffer + index, tftp_options[i].option, buffer_size - index);
               index += strlen(tftp_options[i].option);
               index++;
               Strncpy(buffer + index, tftp_options[i].value, buffer_size - index);
               index += strlen(tftp_options[i].value);
               index++;    
          }
     }
     /* send the buffer */
     result = sendto(socket, buffer, index, 0, (struct sockaddr *)sa,
                     sizeof(*sa));
     if (result < 0)
          return ERR;
     return OK;
}

/*
 *  2 bytes   2 bytes     string   1 byte
 * ---------------------------------------
 *| Opcode  | ErrorCode | ErrMsg |    0   |
 * ---------------------------------------
 */
int tftp_send_error(int socket, struct sockaddr_storage *sa, short err_code,
                    char *buffer, int buffer_size)
{
     int size;
     int result;
     struct tftphdr *tftphdr = (struct tftphdr *)buffer;

     if (err_code > EOPTNEG)
          return ERR;
     tftphdr->th_opcode = htons(ERROR);
     tftphdr->th_code = htons(err_code);
     Strncpy(tftphdr->th_msg, tftp_errmsg[err_code], buffer_size - 4);

     size = 4 + strlen(tftp_errmsg[err_code]) + 1;

     result = sendto(socket, tftphdr, size, 0, (struct sockaddr *)sa,
                     sizeof(*sa));
     if (result < 0)
          return ERR;
     return OK;
}

/*
 *  2 bytes   2 bytes   N bytes
 * ----------------------------
 *| Opcode  | Block # | Data   |
 * ----------------------------
 */
int tftp_send_data(int socket, struct sockaddr_storage *sa, long block_number,
                   int size, char *data)
{
     struct tftphdr *tftphdr = (struct tftphdr *)data;
     int result;

     tftphdr->th_opcode = htons(DATA);
     tftphdr->th_block = htons((short)block_number);

     result = sendto(socket, data, size, 0, (struct sockaddr *)sa,
                     sizeof(*sa));
     if (result < 0)
          return ERR;
     return OK;
}

/*
 * Wait for a packet. This function can listen on 2 sockets. This is
 * needed by the multicast tftp client.
 */
int tftp_get_packet(int sock1, int sock2, int *sock, struct sockaddr_storage *sa,
                    struct sockaddr_storage *sa_from, struct sockaddr_storage *sa_to,
                    int timeout, int *size, char *data)
{
     int result;
     struct timeval tv;
     fd_set rfds;
     struct sockaddr_storage from;
     struct tftphdr *tftphdr = (struct tftphdr *)data;

     struct msghdr msg;         /* used to get client's packet info */
     struct cmsghdr *cmsg;
     struct in_pktinfo *pktinfo4;
     struct in6_pktinfo *pktinfo6;
     struct iovec iov;
     char cbuf[1024];

     /* initialise structure */
     memset(&from, 0, sizeof(from));
     iov.iov_base = data;
     iov.iov_len = *size;
     msg.msg_name = &from;
     msg.msg_namelen = sizeof(from);
     msg.msg_iov = &iov;
     msg.msg_iovlen = 1;
     msg.msg_control = cbuf;
     msg.msg_controllen = sizeof(cbuf);

     /* Wait up to five seconds. */
     tv.tv_sec = timeout;
     tv.tv_usec = 0;

     /* Watch socket to see when it has input. */
     FD_ZERO(&rfds);
     FD_SET(sock1, &rfds);
     if (sock2 > -1)
          FD_SET(sock2, &rfds);

     /* wait for data on sockets */
     result = select(FD_SETSIZE, &rfds, NULL, NULL, &tv);

     switch (result)
     {
     case -1:
          logger(LOG_ERR, "select: %s", strerror(errno));
          return ERR;
     case 0:
          return GET_TIMEOUT;
          break;
     case 1:
     case 2:
          result = 0;

          if (FD_ISSET(sock1, &rfds))
          {
               result = recvmsg(sock1, &msg, 0);               
               if (sock)
                    *sock = sock1;
          }
          else
          {
               if ((sock2 > -1) && (FD_ISSET(sock2, &rfds)))
               {
                    result = recvmsg(sock2, &msg, 0);
                    if (sock)
                         *sock = sock2;
               }
          }
          if (result == 0)
               return ERR;
          if (result == -1)
          {
               logger(LOG_ERR, "recvmsg: %s", strerror(errno));
               return ERR;
          }

          /* if needed read data from message control */
          if (sa_to)
          {
               for (cmsg = CMSG_FIRSTHDR(&msg);
                    cmsg != NULL && cmsg->cmsg_len >= sizeof(*cmsg);
                    cmsg = CMSG_NXTHDR(&msg, cmsg))
               {
#if defined(SOL_IP) && defined(IP_PKTINFO)
                    if (cmsg->cmsg_level == SOL_IP
                        && cmsg->cmsg_type == IP_PKTINFO)
                    {
                         pktinfo4 = (struct in_pktinfo *)CMSG_DATA(cmsg);
                         sa_to->ss_family = AF_INET;
                         ((struct sockaddr_in *)sa_to)->sin_addr =
                              pktinfo4->ipi_addr;
                    }
#endif                    
#if defined(SOL_IPV6) && defined(IPV6_PKTINFO)
                    if (cmsg->cmsg_level == SOL_IPV6
                        && cmsg->cmsg_type == IPV6_PKTINFO)
                    {
                         pktinfo6 = (struct in6_pktinfo *)CMSG_DATA(cmsg);
                         sa_to->ss_family = AF_INET6;
                         ((struct sockaddr_in6 *)sa_to)->sin6_addr =
                              pktinfo6->ipi6_addr;
                    }
#endif
                    break;
               }
          }

          /* return the size to the caller */
          *size = result;

          /* return the peer address/port to the caller */
          if (sa_from != NULL)
               memcpy(sa_from, &from, sizeof(from));

          /* if sa as never been initialised, port is still 0 */
          if (sockaddr_get_port(sa) == 0)
               memcpy(sa, &from, sizeof(from));


          switch (ntohs(tftphdr->th_opcode))
          {
          case RRQ:
               return GET_RRQ;
          case WRQ:
               return GET_WRQ;
          case ACK:
               return GET_ACK;
          case OACK:
               return GET_OACK;
          case ERROR:
               return GET_ERROR;
          case DATA:
               return GET_DATA;
          default:
               return GET_DISCARD;
          }
          break;
     default:
          return ERR;
     }
}

/*
 * Read from file and do netascii conversion if needed
 */
int tftp_file_read(FILE *fp, char *data_buffer, int data_buffer_size, long block_number,
                   int convert, long *prev_block_number, long *prev_file_pos, int *temp)
{
     int c;
     char prevchar = *temp & 0xff;
     char newline = (*temp & 0xff00) >> 8;
     int data_size;

     if (!convert)
     {
	  /* In this case, just read the requested data block.
	     Anyway, in the multicast case it can be in random
	     order. */
	  if (fseek(fp, block_number * data_buffer_size, SEEK_SET) != 0)
	        return ERR;
	  data_size = fread(data_buffer, 1, data_buffer_size, fp);
     }
     else
     {
	  /* 
	   * When converting data, it become impossible to seek in
	   * the file based on the block number. So we must always
	   * remeber the position in the file from were to read the
	   * data requested by the client. Client can only request data
	   * for the same block or the next, but we cannot assume this
	   * block number will increase at every ACK since it can be
	   * lost in transmission.
	   *
	   * The stategy is to remeber the file position as well as
	   * the block number from the current call to this function.
	   * If the client request a block number different from that
           * we return ERR.
	   * 
	   * If the client request many time the same block, the
	   * netascii conversion is done each time. Since this is not
	   * a normal condition it should not be a problem for system
	   * performance.
	   *
	   */
	  if ((block_number != *prev_block_number) && (block_number != *prev_block_number + 1))
	       return ERR;
	  if (block_number == *prev_block_number)
	  {
	       if (fseek(fp, *prev_file_pos, SEEK_SET) != 0)
		     return ERR;
	  }

	  *prev_file_pos = ftell(fp);

	  /*
	   * convert to netascii, based on netkit-tftp-0.17 routine in tftpsubs.c
	   * i index output buffer
	   */
	  for (data_size = 0; data_size < data_buffer_size; data_size++)
	  {
	       if (newline)
	       {
		    if (prevchar == '\n')
			 c = '\n';       /* lf to cr,lf */
		    else
			 c = '\0';       /* cr to cr,nul */
		    newline = 0;
	       }
	       else
	       {
		    c = fgetc(fp);
		    if (c == EOF)
			 break;
		    if (c == '\n' || c == '\r')
		    {
			 prevchar = c;
			 c = '\r';
			 newline = 1;
		    }
	       }
               data_buffer[data_size] = c;
	  }
	  /* save state */
	  *temp = (newline << 8) | prevchar;
     }

     /*
      * Successfull return.
      */
     *prev_block_number = block_number;
     return data_size;
}

/*
 * Write to file and do netascii conversion if needed
 */
int tftp_file_write(FILE *fp, char *data_buffer, int data_buffer_size, long block_number, int data_size,
                    int convert, long *prev_block_number, int *temp)
{
     int bytes_written;
     int c;
     char prevchar = *temp;

     if (!convert)
     {
	  /* Simple case, just seek and write */
          if (fseek(fp, (block_number - 1) * data_buffer_size, SEEK_SET) != 0)
	      return 0;
	  bytes_written = fwrite(data_buffer, 1, data_size, fp);
     }
     else if (block_number != *prev_block_number)
     {
	  /* 
	   * Same principle than for reading, but simpler since when client
           * send same block twice there is no need to rewrite it to the
           * file
	   */
	  if (block_number != *prev_block_number + 1)
	       return ERR;

	  /*
	   * convert to netascii, based on netkit-tftp-0.17 routine in tftpsubs.c
	   * i index input buffer
	   */
	  for (bytes_written = 0; bytes_written < data_size; bytes_written++)
	  {
               c = data_buffer[bytes_written];
               if (prevchar == '\r')
               {
                    if (c == '\n')
                    {
                         fseek(fp, -1, SEEK_CUR); /* cr,lf to lf */
                         if (fputc(c, fp) == EOF)
                              break;
                    }
                    else if (c != '\0')           /* cr,nul to cr */
                    {
                         if (fputc(c, fp) == EOF)
                              break;
                    }
               }
               else
               {
                    if (fputc(c, fp) == EOF)
                         break;
               }
               prevchar = c;
          }

	  /* save state */
	  *temp = prevchar;
     }

     /*
      * Successful return.
      */
     *prev_block_number = block_number;
     return bytes_written;
}

/*
 * Implement block number rollover.  Only applies to unicast.  Wrap_to is
 * what the block number will become once it overflows.  Normally it is 0,
 * but some implementations use 1.
 */
long tftp_rollover_blocknumber(short block_number, long prev_block_number, unsigned short wrap_to)
{
      unsigned short b = (unsigned short)block_number;
      unsigned short pb = (unsigned short)prev_block_number;
      long result = b | (prev_block_number & ~0xFFFF);
      if (b < 0x4000 && pb > 0xC000)
	  result += 0x10000 + wrap_to;
      else if (b > 0xC000 && pb < 0x4000 && (prev_block_number & ~0xFFFF))
	  result -= 0x10000 - wrap_to;
      return result;
}
