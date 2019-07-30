/* hey emacs! -*- Mode: C; c-file-style: "k&r"; indent-tabs-mode: nil -*- */
/*
 * tftp.c
 *    main client file.
 *
 * $Id: tftp.c,v 1.47 2004/03/15 23:55:56 jp Exp $
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
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <string.h>
#include <stdarg.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#include <signal.h>

#if HAVE_READLINE
#include <readline/readline.h>
#include <readline/history.h>
#endif

#if HAVE_ARGZ
#include <argz.h>
#else
#include "argz.h"
#endif

#include "tftp.h"
#include "tftp_io.h"
#include "tftp_def.h"
#include "logger.h"
#include "options.h"

/* Maximum number of args on a line. 20 should be more than enough. */
#define MAXARG  20
/* for readline */
#define HISTORY_FILE ".atftp_history"

/* defined as extern in tftp_file.c and mtftp_file.c, set by the signal
   handler */
int tftp_cancel = 0;

/* local flags */
int interactive = 1;            /* if false, we run in batch mode */
int tftp_result = OK;           /* status of tftp_send_file or
                                   tftp_receive_file, used for status() */

/* Structure to hold some information that must be passed to
 * functions.
 */
struct client_data data;

/* tftp.c local only functions. */
static void signal_handler(int signal);
int read_cmd(void);
#if HAVE_READLINE
# if (HAVE_RL_COMPLETION_MATCHES | HAVE_COMPLETION_MATCHES)
int getc_func(FILE *fp);
char **completion(const char *text, int start, int end);
char *command_generator(const char *text, int state);
# endif
#endif
void make_arg(char *string, int *argc, char ***argv);
int process_cmd(int argc, char **argv);
int tftp_cmd_line_options(int argc, char **argv);
void tftp_usage(void);

/* Functions associated with the tftp commands. */
int set_peer(int argc, char **argv);
int set_mode(int argc, char **argv);
int set_option(int argc, char **argv);
int put_file(int argc, char **argv);
int get_file(int argc, char **argv);
#ifdef HAVE_MTFTP
int mtftp_opt(int argc, char **argv);
#endif
int quit(int argc, char **argv);
int set_verbose(int argc, char **argv);
int set_trace(int argc, char **argv);
int status(int argc, char **argv);
int set_timeout(int argc, char **argv);
int help(int argc, char **argv);

/* All supported commands. */
struct command {
     const char *name;
     int (*func)(int argc, char **argv);
     const char *helpmsg;
} cmdtab[] = {
     {"connect", set_peer, "connect to tftp server"},
     {"mode", set_mode, "set file transfer mode (netascii/octet)"},
     {"option", set_option, "set RFC1350 options"},
     {"put", put_file, "upload a file to the host"},
     {"get", get_file, "download a file from the host"},
#ifdef HAVE_MTFTP
     {"mtftp", mtftp_opt, "set mtftp variables"},
     {"mget", get_file, "download file from mtftp server"},
#endif
     {"quit", quit, "exit tftp"},
     {"verbose", set_verbose, "toggle verbose mode"},
     {"trace", set_trace, "toggle trace mode"},
     {"status", status, "print status information"},
     {"timeout", set_timeout, "set the timeout before a retry"},
     {"help", help, "print help message"},
     {"?", help, "print help message"},
     {NULL, NULL, NULL}
};

/*
 * Open the socket, register signal handler and
 * pass the control to read_cmd.
 */
int main(int argc, char **argv)
{
     /* Allocate memory for data buffer. */
     if ((data.data_buffer = malloc((size_t)SEGSIZE+4)) == NULL)
     {
          fprintf(stderr, "tftp: memory allcoation failed.\n");
          exit(ERR);
     }
     data.data_buffer_size = SEGSIZE + 4;

     /* Allocate memory for tftp option structure. */
     if ((data.tftp_options =
          malloc(sizeof(tftp_default_options))) == NULL)
     {
          fprintf(stderr, "tftp: memory allocation failed.\n");
          exit(ERR);
     }
     /* Copy default options. */
     memcpy(data.tftp_options, tftp_default_options,
            sizeof(tftp_default_options));

     /* Allocate memory for tftp option reply from server. */
     if ((data.tftp_options_reply =
          malloc(sizeof(tftp_default_options))) == NULL)
     {
          fprintf(stderr, "tftp: memory allocation failed.\n");
          exit(ERR);
     }
     /* Copy default options. */
     memcpy(data.tftp_options_reply, tftp_default_options,
            sizeof(tftp_default_options));

     /* default options  */
#ifdef HAVE_MTFTP
     data.mtftp_client_port = 76;
     Strncpy(data.mtftp_mcast_ip, "0.0.0.0", MAXLEN);
     data.mtftp_listen_delay = 2;
     data.mtftp_timeout_delay = 2;
#endif
     data.timeout = TIMEOUT;
     data.checkport = 1;
     data.trace = 0;
     data.verbose = 0;
#ifdef DEBUG
     data.delay = 0;
#endif

     /* register SIGINT -> C-c */
     signal(SIGINT, signal_handler);
     signal(SIGTERM, signal_handler);

     /* parse options, and maybe run in non interractive mode */
     tftp_cmd_line_options(argc, argv);

     if (interactive)
          return read_cmd();
     return OK;
}

/*
 * When we receive a signal, we set tftp_cancel in order to
 * abort ongoing transfer.
 */
void signal_handler(int signal)
{
     /*
      * if receiving or sending files, we should abort
      * and send and error ACK
      */
     tftp_cancel = 1;
}

/*
 * Read commands with a nice prompt and history (if compile with
 * libreadline. Otherway we only get the basic.
 */
int read_cmd(void)
{
     int run = 1;
#if HAVE_READLINE
     char *string = NULL;
#else
     char string[MAXLEN];
#endif
     int argc;
     char **argv = NULL;
#if HAVE_READLINE
     char history[MAXLEN];

     if (getenv("HOME") != NULL)
          snprintf(history, sizeof(history), "%s/%s", getenv("HOME"), HISTORY_FILE);
     else
          snprintf(history, sizeof(history), "%s", HISTORY_FILE);

# if (HAVE_RL_COMPLETION_MATCHES | HAVE_COMPLETION_MATCHES)
     rl_attempted_completion_function = completion;
     rl_getc_function = getc_func;
# endif
#endif

#if HAVE_READLINE
     using_history();
     read_history(history);
#endif

     while (run)
     {
#if HAVE_READLINE
          if ((string = readline("tftp> ")) == NULL)
          {
               fprintf(stderr, "\n");
               break;
          }
#else
          fprintf(stderr, "tftp> ");
          if (fgets(string, MAXLEN, stdin) == NULL)
          {
               fprintf(stderr, "\n");
               break;
          }
#endif
          else
          {
#ifndef HAVE_READLINE
               string[strlen(string)-1] = 0;
#endif
               if (strlen(string) != 0)
               {
                    make_arg(string, &argc, &argv);
                    if (argc > 0)
                    {
#if HAVE_READLINE
                         add_history(string);
#endif
                         if (process_cmd(argc, argv) == QUIT)
                              run = 0;
                    }
#if HAVE_READLINE
                    free(string);
#endif
               }
          }
     }

#if HAVE_READLINE
     /* save history */
     write_history(history);
#endif

     return 0;
}

#if HAVE_READLINE
# if (HAVE_RL_COMPLETION_MATCHES | HAVE_COMPLETION_MATCHES)
int getc_func(FILE *fp)
{
     fd_set rfds;

     FD_ZERO(&rfds);
     FD_SET(fileno(fp), &rfds);

     if (select(FD_SETSIZE, &rfds, NULL, NULL, NULL) < 0)
     {
          rl_kill_full_line(0,0);
          return '\n';
     }
     return rl_getc(fp);
}

char **completion(const char *text, int start, int end)
{
     char **matches;

     matches = (char **)NULL;

     /* If this word is at the start of the line, then it is a command
        to complete.  Otherwise it is the name of a file in the current
        directory. */
     if (start == 0)
#if HAVE_RL_COMPLETION_MATCHES
          matches = rl_completion_matches(text, command_generator);
#endif
#if HAVE_COMPLETION_MATCHES
          matches = completion_matches(text, command_generator);
#endif
     return (matches);
}

/* Generator function for command completion.  STATE lets us
   know whether to start from scratch; without any state
   (i.e. STATE == 0), then we start at the top of the list. */
char *command_generator(const char *text, int state)
{
     static int list_index, len;
     char *name;

     /* If this is a new word to complete, initialize now.  This
        includes saving the length of TEXT for efficiency, and
        initializing the index variable to 0. */
     if (!state)
     {
          list_index = 0;
          len = strlen (text);
     }
     /* Return the next name which partially matches from the
        command list. */
     while ((name = (char *)cmdtab[list_index].name))
     {
          list_index++;

          if (strncmp (name, text, len) == 0)
               return strdup(name);
     }

     /* If no names matched, then return NULL. */
     return NULL;
}
# endif
#endif

/*
 * set argc/argv from variadic string arguments
*/
void make_arg_vector(int *argc, char***argv, ...)
{
  char **p;
  char *s;
  va_list argp;

  // how many args?
  *argc = 0;
  va_start(argp, argv);
  while ( (s=va_arg(argp, char*)) )
    ++*argc;

  // allocate storage
  *argv = malloc(*argc * sizeof (char*));

  // store args
  p = *argv;
  va_start(argp, argv);
  while ( (s=va_arg(argp, char*)) )
    *p++ = s;
}

/*
 * Split a string into args.
 */
void make_arg(char *string, int *argc, char ***argv)
{
     static char *tmp = NULL;
     size_t argz_len;

     /* split the string to an argz vector */
     if (argz_create_sep(string, ' ', &tmp, &argz_len) != 0)
     {
          *argc = 0;
          return;
     }
     /* retreive the number of arguments */
     *argc = argz_count(tmp, argz_len);
     /* give enough space for all arguments to **argv */
     if ((*argv = realloc(*argv,  (*argc + 1) * sizeof(char *))) == NULL)
     {
          *argc = 0;
          return;
     }
     /* extract arguments */
     argz_extract(tmp, argz_len, *argv);

     /* if the last argument is an empty string ... it happens
        when some extra space are added at the end of string :( */
     if (strlen((*argv)[*argc - 1]) == 0)
          *argc = *argc - 1;
}

/*
 * Once a line have been read and splitted, find the corresponding
 * function and call it.
 */
int process_cmd(int argc, char **argv)
{
     int i = 0;

     /* find the command in the command table */
     while (1)
     {
          if (cmdtab[i].name == NULL)
          {
               fprintf(stderr, "tftp: bad command name.\n");
               return 0;
          }
          if (strcasecmp(cmdtab[i].name, argv[0]) == 0)
          {
               return (cmdtab[i].func)(argc, argv);
          }
          i++;
     }
}

/*
 * Update sa_peer structure, hostname and port number adequately
 */
int set_peer(int argc, char **argv)
{
     struct addrinfo hints, *addrinfo;
     int err;

     /* sanity check */
     if ((argc < 2) || (argc > 3))
     {
          fprintf(stderr, "Usage: %s host-name [port]\n", argv[0]);
          return ERR;
     }

     /* look up the service and host */
     memset(&hints, 0, sizeof(hints));
     hints.ai_socktype = SOCK_DGRAM;
     hints.ai_flags = AI_CANONNAME;
     err = getaddrinfo(argv[1], argc == 3 ? argv[2] : "tftp",
                       &hints, &addrinfo);
     /* if valid, update s_inn structure */
     if (err == 0)
          err = sockaddr_set_addrinfo(&data.sa_peer, addrinfo);
     if (err == 0)
     {
          Strncpy(data.hostname, addrinfo->ai_canonname,
                  sizeof(data.hostname));
          data.hostname[sizeof(data.hostname)-1] = 0;
          freeaddrinfo(addrinfo);
     }
     else
     {
          if (err == EAI_SERVICE)
          {
               if (argc == 3)
                    fprintf(stderr, "%s: bad port number.\n", argv[2]);
               else
                    fprintf(stderr, "tftp: udp/tftp, unknown service.\n");
          }
          else
          {
               fprintf(stderr, "tftp: unknown host %s.\n", argv[1]);
          }
          data.connected = 0;
          return ERR;
     }
     /* copy port number to data structure */
     data.port = sockaddr_get_port(&data.sa_peer);

     data.connected = 1;
     return OK;
}

/*
 * Set the mode to netascii or octet
 */
int set_mode(int argc, char **argv)
{
     if (argc > 2)
     {
          fprintf(stderr, "Usage: %s [netascii] [octet]\n", argv[0]);
          return ERR;
     }
     if (argc == 1)
     {
          fprintf(stderr, "Current mode is %s.\n",
                  data.tftp_options[OPT_MODE].value);
          return OK;
     }
     if (strcasecmp("netascii", argv[1]) == 0)
          Strncpy(data.tftp_options[OPT_MODE].value, "netascii",
                  VAL_SIZE);
     else if (strcasecmp("octet", argv[1]) == 0)
          Strncpy(data.tftp_options[OPT_MODE].value, "octet",
                  VAL_SIZE);
     else
     {
          fprintf(stderr, "tftp: unkowned mode %s.\n", argv[1]);
          fprintf(stderr, "Usage: %s [netascii] [octet]\n", argv[0]);
          return ERR;
     }
     return OK;
}

/*
 * Set an option
 */
int set_option(int argc, char **argv)
{
     char value[VAL_SIZE];

     /* if there are no arguments */
     if ((argc < 2) || (argc > 3))
     {
          fprintf(stderr, "Usage: option <option name> [option value]\n");
          fprintf(stderr, "       option disable <option name>\n");
          if (data.tftp_options[OPT_TSIZE].specified)
               fprintf(stderr, "  tsize:     enabled\n");
          else
               fprintf(stderr, "  tsize:     disabled\n");
          if (data.tftp_options[OPT_BLKSIZE].specified)
               fprintf(stderr, "  blksize:   %s\n",
                       data.tftp_options[OPT_BLKSIZE].value);
          else
               fprintf(stderr, "  blksize:   disabled\n");
          if (data.tftp_options[OPT_TIMEOUT].specified)
               fprintf(stderr, "  timeout:   %s\n",
                       data.tftp_options[OPT_TIMEOUT].value);
          else
               fprintf(stderr, "  timeout:   disabled\n");
          if (data.tftp_options[OPT_MULTICAST].specified)
               fprintf(stderr, "  multicast: enabled\n");
          else
               fprintf(stderr, "  multicast: disabled\n");
          if (data.tftp_options[OPT_PASSWORD].specified)
               fprintf(stderr, "   password: enabled\n");
          else
               fprintf(stderr, "   password: disabled\n");
          return ERR;
     }
     /* if disabling an option */
     if (strcasecmp("disable", argv[1]) == 0)
     {
          if (argc != 3)
          {
               fprintf(stderr, "Usage: option disable <option name>\n");
               return ERR;
          }
          /* disable it */
          if (opt_disable_options(data.tftp_options, argv[2]) == ERR)
          {
               fprintf(stderr, "no option named %s\n", argv[2]);
               return ERR;
          }
          if (opt_get_options(data.tftp_options, argv[1], value) == ERR)
               fprintf(stderr, "Option %s disabled\n", argv[2]);
          else
               fprintf(stderr, "Option %s = %s\n", argv[1], value);
          return OK;
     }

     /* ok, we are setting an argument */
     if (argc == 2)
     {
          if (opt_set_options(data.tftp_options, argv[1], NULL) == ERR)
          {
               fprintf(stderr, "no option named %s\n", argv[1]);
               return ERR;
          }
     }
     if (argc == 3)
     {
          if (opt_set_options(data.tftp_options, argv[1], argv[2]) == ERR)
          {
               fprintf(stderr, "no option named %s\n", argv[1]);
               return ERR;
          }
     }
     /* print the new value for that option */
     if (opt_get_options(data.tftp_options, argv[1], value) == ERR)
          fprintf(stderr, "Option %s disabled\n", argv[1]);
     else
          fprintf(stderr, "Option %s = %s\n", argv[1], value);
     return OK;
}

/*
 * Put a file to the server.
 */
int put_file(int argc, char **argv)
{
     socklen_t len = sizeof(data.sa_local);

     if ((argc < 2) || (argc > 3))
     {
          fprintf(stderr, "Usage: put local_file [remote_file]\n");
          return ERR;
     }
     if (!data.connected)
     {
          fprintf(stderr, "Not connected.\n");
          return ERR;
     }
     if (argc == 2)
     {
          Strncpy(data.local_file, argv[1], VAL_SIZE);
          Strncpy(data.tftp_options[OPT_FILENAME].value, argv[1], VAL_SIZE);
     }
     else
     {
          Strncpy(data.local_file, argv[1], VAL_SIZE);
          Strncpy(data.tftp_options[OPT_FILENAME].value, argv[2], VAL_SIZE);
     }

     /* open a UDP socket */
     data.sockfd = socket(data.sa_peer.ss_family, SOCK_DGRAM, 0);
     if (data.sockfd < 0) {
          perror("tftp: ");
          exit(ERR);
     }
     memset(&data.sa_local, 0, sizeof(data.sa_local));
     bind(data.sockfd, (struct sockaddr *)&data.sa_local,
          sizeof(data.sa_local));
     getsockname(data.sockfd, (struct sockaddr *)&data.sa_local, &len);

     /* do the transfer */
     gettimeofday(&data.start_time, NULL);
     tftp_result = tftp_send_file(&data);
     gettimeofday(&data.end_time, NULL);

     /* close the socket */
     fsync(data.sockfd);
     close(data.sockfd);

     return tftp_result;
}

/*
 * Receive a file from the server.
 */
int get_file(int argc, char **argv)
{
#if HAVE_READLINE
     char *string;
#else
     char string[MAXLEN];
#endif
#ifdef HAVE_MTFTP
     int use_mtftp;
#endif
     char *tmp;
     FILE *fp;
     socklen_t len = sizeof(data.sa_local);

#ifdef HAVE_MTFTP
     if (strcmp(argv[0], "mget") == 0)
          use_mtftp = 1;
     else
          use_mtftp = 0;
#endif

     if ((argc < 2) || (argc > 3))
     {
          fprintf(stderr, "Usage: %s remote_file [local_file]\n", argv[0]);
          return ERR;
     }
     if (!data.connected)
     {
          fprintf(stderr, "Not connected.\n");
          return ERR;
     }
     if (argc == 2)
     {
          Strncpy(data.tftp_options[OPT_FILENAME].value,
                  argv[1], VAL_SIZE);
          tmp = strrchr(argv[1], '/');
          if (tmp < argv[1])
               tmp = argv[1];
          else
               tmp++;
          Strncpy(data.local_file, tmp, VAL_SIZE);
     }
     else
     {
          Strncpy(data.local_file, argv[2], VAL_SIZE);
          Strncpy(data.tftp_options[OPT_FILENAME].value, argv[1], VAL_SIZE);
     }

     /* if interractive, verify if localfile exists */
     if (interactive)
     {
          /* if localfile if stdout, nothing to verify */
          if (strncmp(data.local_file, "/dev/stdout", VAL_SIZE) != 0)
          {
               if ((fp = fopen(data.local_file, "r")) != NULL)
               {
                    fclose(fp);
#if HAVE_READLINE
                    string = readline("Overwite local file [y/n]? ");
#else
                    fprintf(stderr, "Overwite local file [y/n]? ");
                    fgets(string, MAXLEN, stdin);
                    string[strlen(string) - 1] = 0;
#endif
                    if (!(strcasecmp(string, "y") == 0))
                    {
#if HAVE_READLINE
                         free(string);
#endif
                         return OK;
                    }
#if HAVE_READLINE
                    free(string);
#endif
               }
          }
     }

     /* open a UDP socket */
     data.sockfd = socket(data.sa_peer.ss_family, SOCK_DGRAM, 0);
     if (data.sockfd < 0) {
          perror("tftp: ");
          exit(ERR);
     }
     memset(&data.sa_local, 0, sizeof(data.sa_local));
     bind(data.sockfd, (struct sockaddr *)&data.sa_local,
          sizeof(data.sa_local));
     getsockname(data.sockfd, (struct sockaddr *)&data.sa_local, &len);

     /* do the transfer */
     gettimeofday(&data.start_time, NULL);
#ifdef HAVE_MTFTP
     if (use_mtftp)
          tftp_result = tftp_mtftp_receive_file(&data);
     else
#endif
          tftp_result = tftp_receive_file(&data);

     gettimeofday(&data.end_time, NULL);

     /* close the socket */
     fsync(data.sockfd);
     close(data.sockfd);

     return tftp_result;
}

#ifdef HAVE_MTFTP
/*
 * Set ot get mtftp variable value
 */
int mtftp_opt(int argc, char **argv)
{
     if (argc != 3)
     {
          fprintf(stderr, "Usage: mtftp <option name> <option value>\n");
          /* print current value of variables */
          fprintf(stderr, "  client-port:   %d\n", data.mtftp_client_port);
          fprintf(stderr, "  mcast-ip:      %s\n", data.mtftp_mcast_ip);
          fprintf(stderr, "  listen-delay:  %d\n", data.mtftp_listen_delay);
          fprintf(stderr, "  timeout-delay: %d\n", data.mtftp_timeout_delay);
     }
     else
     {
          if (strcmp(argv[1], "client-port") == 0)
          {
               data.mtftp_client_port = atoi(argv[2]);
               fprintf(stderr, "mtftp client-port = %d\n",
                       data.mtftp_client_port);
          }
          else if (strcmp(argv[1], "mcast-ip") == 0)
          {
               Strncpy(data.mtftp_mcast_ip, argv[2], MAXLEN);
               fprintf(stderr, "mtftp mcast-ip = %s\n", data.mtftp_mcast_ip);
          }
          else if (strcmp(argv[1], "listen-delay") == 0)
          {
               data.mtftp_listen_delay = atoi(argv[2]);
               fprintf(stderr, "mtftp listen-delay = %d\n",
                       data.mtftp_listen_delay);
          }
          else if (strcmp(argv[1], "timeout-delay") == 0)
          {
               data.mtftp_timeout_delay = atoi(argv[2]);
               fprintf(stderr, "mtftp timeout-delay = %d\n",
                       data.mtftp_timeout_delay);
          }
          else
          {
               fprintf(stderr, "no mtftp variable named %s\n", argv[1]);
               return ERR;
          }
     }
     return OK;
}

#endif

/*
 * Exit tftp
 */
int quit(int argc, char **argv)
{
     return QUIT;
}

int set_verbose(int argc, char **argv)
{
     if (data.verbose)
     {
          data.verbose = 0;
          fprintf(stderr, "Verbose mode off.\n");
     }
     else
     {
          data.verbose = 1;
          fprintf(stderr, "Verbose mode on.\n");
     }
     return OK;
}

int set_trace(int argc, char **argv)
{
     if (data.trace)
     {
          data.trace = 0;
          fprintf(stderr, "Trace mode off.\n");
     }
     else
     {
          data.trace = 1;
          fprintf(stderr, "Trace mode on.\n");
     }
     return OK;
}

int status(int argc, char **argv)
{
     struct timeval tmp;
#if HAVE_READLINE
     HIST_ENTRY *history = history_get(history_length-1);
#endif
     char string[MAXLEN];

     timeval_diff(&tmp, &data.end_time, &data.start_time);

     if (!data.connected)
          fprintf(stderr, "Not connected\n");
     else
          fprintf(stderr, "Connected:  %s port %d\n", data.hostname,
                  data.port);
     fprintf(stderr, "Mode:       %s\n", data.tftp_options[OPT_MODE].value);
     if (data.verbose)
          fprintf(stderr, "Verbose:    on\n");
     else
          fprintf(stderr, "Verbose:    off\n");
     if (data.trace)
          fprintf(stderr, "Trace:      on\n");
     else
          fprintf(stderr, "Trace:      off\n");
     fprintf(stderr, "Options\n");
     if (data.tftp_options[OPT_TSIZE].specified)
          fprintf(stderr, " tsize:     enabled\n");
     else
          fprintf(stderr, " tsize:     disabled\n");
     if (data.tftp_options[OPT_BLKSIZE].specified)
          fprintf(stderr, " blksize:   enabled\n");
     else
          fprintf(stderr, " blksize:   disabled\n");
     if (data.tftp_options[OPT_TIMEOUT].specified)
          fprintf(stderr, " timeout:   enabled\n");
     else
          fprintf(stderr, " timeout:   disabled\n");
     if (data.tftp_options[OPT_MULTICAST].specified)
          fprintf(stderr, " multicast: enabled\n");
     else
          fprintf(stderr, " multicast: disabled\n");
#ifdef HAVE_MTFTP
     fprintf(stderr, "mtftp variables\n");
     fprintf(stderr, " client-port:   %d\n", data.mtftp_client_port);
     fprintf(stderr, " mcast-ip:      %s\n", data.mtftp_mcast_ip);
     fprintf(stderr, " listen-delay:  %d\n", data.mtftp_listen_delay);
     fprintf(stderr, " timeout-delay: %d\n", data.mtftp_timeout_delay);
#endif
#if HAVE_READLINE
     if (history)
          fprintf(stderr, "Last command: %s\n", history->line);
     else
          fprintf(stderr, "Last command: %s\n", "---");
#endif

     if (strlen(data.tftp_options[OPT_FILENAME].value) > 0)
     {
          fprintf(stderr, "Last file: %s\n",
                  data.tftp_options[OPT_FILENAME].value);
          if (tftp_result == OK)
          {
               print_eng((double)data.file_size, string, sizeof(string), "%3.3f%cB");
               fprintf(stderr, "  Bytes transfered:  %s\n", string);
               fprintf(stderr, "  Time of transfer: %8.3fs\n",
                       (double)(tmp.tv_sec + tmp.tv_usec * 1e-6));
               fprintf(stderr, "  Throughput:        ");
               print_eng((data.file_size /
                          (double)(tmp.tv_sec + tmp.tv_usec * 1e-6)),
                         string, sizeof(string), "%3.3f%cB/s\n");
               fprintf(stderr, "%s", string);
          }
          else
               fprintf(stderr, "  Transfer aborted\n");
     }
     return OK;
}

int set_timeout(int argc, char **argv)
{
     if (argc == 1)
          fprintf(stderr, "Timeout set to %d seconds.\n", data.timeout);
     if (argc == 2)
          data.timeout = atoi(argv[1]);
     if (argc > 2)
     {
          fprintf(stderr, "Usage: timeout [value]\n");
          return ERR;
     }
     return OK;
}

int help(int argc, char **argv)
{
     int i = 0;

     if (argc == 1)
     {
          /* general help */
          fprintf(stderr, "Available command are:\n");
          while (cmdtab[i].name != NULL)
          {
               fprintf(stderr, "%s\t\t%s\n", cmdtab[i].name,
                       cmdtab[i].helpmsg);
               i++;
          }
     }
     if (argc > 1)
     {
          while (cmdtab[i].name != NULL)
          {
               if (strcasecmp(cmdtab[i].name, argv[1]) == 0)
                    fprintf(stderr, "%s: %s\n", cmdtab[i].name,
                            cmdtab[i].helpmsg);
               i++;
          }
     }
     return OK;
}

#define PUT  1
#define GET  2
#define MGET 3

/*
 * If tftp is called with --help, usage is printed and we exit.
 * With --version, version is printed and we exit too.
 * if --get --put --remote-file or --local-file is set, it imply non
 * interactive invocation of tftp.
 */
int tftp_cmd_line_options(int argc, char **argv)
{
     int c;
     int ac;                    /* to format arguments for process_cmd */
     char **av = NULL;          /* same */
     char string[MAXLEN];
     char local_file[MAXLEN] = "";
     char remote_file[MAXLEN] = "";
     int action = 0;

     int option_index = 0;
     static struct option options[] = {
          { "get", 0, NULL, 'g'},
#ifdef HAVE_MTFTP
          { "mget", 0, NULL, 'G'},
#endif
          { "put", 0, NULL, 'p'},
          { "local-file", 1, NULL, 'l'},
          { "remote-file", 1, NULL, 'r'},
          { "password", 1, NULL, 'P'},
          { "tftp-timeout", 1, NULL, 'T'},
          { "mode", 1, NULL, 'M'},
          { "option", 1, NULL, 'O'},
#if 1
          { "timeout", 1, NULL, 't'},
          { "blksize", 1, NULL, 'b'},
          { "tsize", 0, NULL, 's'},
          { "multicast", 0, NULL, 'm'},
#endif
          { "mtftp", 1, NULL, '1'},
          { "no-source-port-checking", 0, NULL, '0'},
          { "verbose", 0, NULL, 'v'},
          { "trace", 0, NULL, 'd'},
#if DEBUG
          { "delay", 1, NULL, 'D'},
#endif
          { "version", 0, NULL, 'V'},
          { "help", 0, NULL, 'h' },
          { 0, 0, 0, 0 }
     };

     /* Support old argument until 0.8 */
     while ((c = getopt_long(argc, argv, /*"gpl:r:Vh"*/ "gpl:r:Vht:b:smP:",
                             options, &option_index)) != EOF)
     {
          switch (c)
          {
          case 'g':
               interactive = 0;
               if ((action == PUT) || (action == MGET))
               {
                    fprintf(stderr, "two actions specified!\n");
                    exit(ERR);
               }
               else
                    action = GET;
               break;
          case 'G':
               interactive = 0;
               if ((action == PUT) || (action == GET))
               {
                    fprintf(stderr, "two actions specified!\n");
                    exit(ERR);
               }
               else
                    action = MGET;
               break;
          case 'p':
               interactive = 0;
               if ((action == GET) || (action == MGET))
               {
                    fprintf(stderr, "two actions specified!\n");
                    exit(ERR);
               }
               else
                    action = PUT;
               break;
          case 'P':
               snprintf(string, sizeof(string), "option password %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'l':
               interactive = 0;
               Strncpy(local_file, optarg, MAXLEN);
               break;
          case 'r':
               interactive = 0;
               Strncpy(remote_file, optarg, MAXLEN);
               break;
          case 'T':
               snprintf(string, sizeof(string), "timeout %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'M':
               snprintf(string, sizeof(string), "mode %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'O':
               snprintf(string, sizeof(string), "option %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case '1':
               snprintf(string, sizeof(string), "mtftp %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
#if 1
          case 't':
               fprintf(stderr, "--timeout deprecated, use --option instead\n");
               snprintf(string, sizeof(string), "option timeout %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'b':
               fprintf(stderr, "--blksize deprecated, use --option instead\n");
               snprintf(string, sizeof(string), "option blksize %s", optarg);
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 's':
               fprintf(stderr, "--tsize deprecated, use --option instead\n");
               snprintf(string, sizeof(string), "option tsize");
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'm':
               fprintf(stderr,
                       "--multicast deprecated, use --option instead\n");
               snprintf(string, sizeof(string), "option multicast");
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
#endif
          case '0':
               data.checkport = 0;
               break;
          case 'v':
               snprintf(string, sizeof(string), "verbose on");
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
          case 'd':
               snprintf(string, sizeof(string), "trace on");
               make_arg(string, &ac, &av);
               process_cmd(ac, av);
               break;
#if DEBUG
          case 'D':
               data.delay = atoi(optarg);
               break;
#endif
          case 'V':
               fprintf(stderr, "atftp-%s (client)\n", VERSION);
               exit(OK);
          case 'h':
               tftp_usage();
               exit(OK);
          case '?':
               tftp_usage();
               exit(ERR);
               break;
          }
     }

     /* verify that one or two arguements are left, they are the host name
        and port */
     /* optind point to the first non option caracter */
     if (optind < (argc - 2))
     {
          tftp_usage();
          exit(ERR);
     }

     if (optind != argc)
     {
          if (optind == (argc - 1))
               snprintf(string, sizeof(string), "connect %s", argv[optind]);
          else
               snprintf(string, sizeof(string), "connect %s %s", argv[optind],
                                       argv[optind+1]);
          make_arg(string, &ac, &av);
          process_cmd(ac, av);
     }

     if (!interactive)
     {
          if (action == PUT)
          {
               if(strlen(remote_file) == 0)
               {
                   strncpy(remote_file, local_file, MAXLEN);
               }
               make_arg_vector(&ac,&av,"put",local_file,remote_file,NULL);
          }
          else if (action == GET)
          {
               if(strlen(local_file) == 0)
               {
                   strncpy(local_file, remote_file, MAXLEN);
               }
               make_arg_vector(&ac,&av,"get",remote_file,local_file,NULL);
          }
          else if (action == MGET)
          {
               if(strlen(local_file) == 0)
               {
                   strncpy(local_file, remote_file, MAXLEN);
               }
               make_arg_vector(&ac,&av,"mget",remote_file,local_file,NULL);
          }
          else
          {
               fprintf(stderr, "No action specified in batch mode!\n");
               exit(ERR);
          }
          if (process_cmd(ac, av) == ERR)
               exit(ERR);
     }
     return OK;
}

void tftp_usage(void)
{
     fprintf(stderr,
             "Usage: tftp [options] [host] [port]\n"
             " [options] may be:\n"
             "  -g, --get                : get file\n"
#ifdef HAVE_MTFTP
             "      --mget               : get file using mtftp\n"
#endif
             "  -p, --put                : put file\n"
             "  -l, --local-file <file>  : local file name\n"
             "  -r, --remote-file <file> : remote file name\n"
             "  -P, --password <password>: specify password (Linksys extension)\n"
             "  --tftp-timeout <value>   : delay before retransmission, client side\n"
#if 0
             "  t, --timeout <value>      : delay before retransmission, "
                                           "server side (RFC2349)\n"
             "  b, --blocksize <value>    : specify blksize to use (RFC2348)\n"
             "  s, --tsize                : use 'tsize' (RFC2349)\n"
             "  m, --multicast            : use 'multicast' (RFC2090)\n"
#endif
             "  --option <\"name value\">  : set option name to value\n"
#ifdef HAVE_MTFTP
             "  --mtftp <\"name value\">   : set mtftp variable to value\n"
#endif
             "  --no-source-port-checking: violate RFC, see man page\n"
             "  --verbose                : set verbose mode on\n"
             "  --trace                  : set trace mode on\n"
#if DEBUG
             "  --delay                  : add delay in state machine for debugging\n"
#endif
             "  -V, --version            : print version information\n"
             "  -h, --help               : print this help\n"
             "\n"
             " [host] is the tftp server name\n"
             " [port] is the port to use\n"
             "\n");
}
