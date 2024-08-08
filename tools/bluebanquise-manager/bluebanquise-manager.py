import sys,time
import yaml
import os
from rich.traceback import install
import textwrap
import validators
import zoneinfo
import json

install(show_locals=True)

# https://theasciicode.com.ar/extended-ascii-code/box-drawings-single-line-horizontal-vertical-character-ascii-code-197.html
# https://misc.flogisoft.com/bash/tip_colors_and_formatting


class windows_manager(object):
  """ This is a small windows manager for terminal.
  I hate things that clear the terminal because it often clears logs or errors.
  So this is an home made concept of windows manager that lives verticaly in the terminal :)
  """

  def __init__(self, init_nesting_level=-1):
    self.w_nesting_level = init_nesting_level
    #self.w_colors = ['39', '214', '201', '226']
    self.w_colors = ['226', '208', '196', '163']
    self.w_allowed_colors = {
      'blue': '\033[94m',
      'green': '\033[92m',
      'reset': '\033[0m'
    }

  def t_green(self, message):
    return self.w_allowed_colors['green'] + message + self.w_allowed_colors['reset']

  def t_blue(self, message):
    return self.w_allowed_colors['blue'] + message + self.w_allowed_colors['reset']

  def w_sprint(self, message, nl=True):
    # Now we have to parse text lines by lines, and decorate it
    # We use native decorator, but we have to complete each line with spaces
    umessage = []
    for line in message.splitlines():
      umessage.append(self.w_decorator_left_right(line, force_nesting_level = self.w_nesting_level + 1, fill_line = True))
    message = '\n'.join(umessage)
    if nl:
      message = message + '\n'
    for c in message:
      sys.stdout.write(c)
      sys.stdout.flush()
      if c != " ":
        time.sleep(1./500)

  def w_input(self, message, nl=True):
    umessage = self.w_decorator_left_right(message, force_nesting_level = self.w_nesting_level + 1, no_right = True)
    answer = input(umessage)
    # https://stackoverflow.com/questions/12586601/remove-last-stdout-line-in-python
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
    print(self.w_decorator_left_right(message + str(answer), force_nesting_level = self.w_nesting_level + 1, fill_line = True))
    return answer

  def w_create(self, w_title=None):
    self.w_sprint("\n")
    # Get size of terminal
    # We do that each time to cover terminal resized during usage
    columns = os.get_terminal_size().columns
    # Set lead section depending if we are creating or closing a window
    # This is of size 5
    lead = "╭─────"
    self.w_nesting_level = self.w_nesting_level + 1
    # Create current windows frame
    box = "\033[38;5;" + self.w_colors[self.w_nesting_level] + "m" + lead
    # Manage title if any
    if w_title is not None:
      box = box + " " + str(w_title) + " "
      title_size = len(w_title) + 2
    else:
      title_size = 0
    # Complete the line
    for i in range(1, columns - self.w_nesting_level * 4 * 2 - len(lead) - title_size - 1, 1):
      box = box + "─"
    box = box + "╮" + "\033[0m"
    box = self.w_decorator_left_right(box)
    print(box)

  def w_destroy(self):
    # Get size of terminal
    # We do that each time to cover terminal resized during usage
    columns = os.get_terminal_size().columns
    # Set lead section depending if we are creating or closing a window
    # This is of size 5
    lead = "╰─────"
    # Create current windows frame
    box = "\033[38;5;" + self.w_colors[self.w_nesting_level] + "m" + lead
    # Complete the line
    for i in range(1, columns - self.w_nesting_level * 4 * 2 - len(lead) - 1, 1):
      box = box + "─"
    box = box + "╯" + "\033[0m"
    box = self.w_decorator_left_right(box)
    print(box)
    self.w_nesting_level = self.w_nesting_level - 1

  def w_decorator_left_right(self, message, force_nesting_level=None, fill_line=False, no_right=False):
    if force_nesting_level is not None:
      nesting_level = force_nesting_level
    else:
      nesting_level = self.w_nesting_level
    buffer = ""
    for nl in range(0, nesting_level, 1):
      buffer = buffer + "\033[38;5;" + self.w_colors[nl] + "m│\033[0m   "
    message = buffer + message
    buffer = ""
    if not no_right:
      for nl in range(nesting_level-1, -1, -1):
        buffer = buffer + "\033[38;5;" + self.w_colors[nl] + "m   │\033[0m"
      # Before applying right buffer, lets check if line must be filled
      if fill_line:
        columns = os.get_terminal_size().columns
        message_buffer = (message + buffer)
        message_buffer = message_buffer.replace("\033[0m", "")
        for i in self.w_colors:
          message_buffer = message_buffer.replace("\033[38;5;" + str(i) + "m", "")
        for i, v in self.w_allowed_colors.items():
          message_buffer = message_buffer.replace(v, "")
        for i in range(1, columns - len(message_buffer), 1):
          message = message + " "

      message = message + buffer
    return message

print("""\

              (o_
    (o_  (o_  //\\
    (/)_ (/)_ V_/_

  BlueBanquise manager
  v1.0.0
  https://github.com/bluebanquise/bluebanquise/""")

wm = windows_manager()

wm.w_create(w_title="BlueBanquise manager")

answer = 0
while True:

  menu_message = """
  - Manage inventory -
  1. Global parameters
  2. Groups (function, os, hardware, ...)
  3. Nodes

  - Manage nodes -
  4. Deploy nodes OS
  5. Deploy nodes configuration
  6. Nodes hardware operations (power, console, ...)

  9. Exit

  """
  wm.w_sprint(textwrap.dedent(menu_message))
  answer = int(wm.w_input("❱❱❱ "))
#  answer = int(input(wm.w_rprint("❱❱❱ ")))

  if answer == 9:
    wm.w_sprint("-- Exiting. Have a nice day :)")
    wm.w_destroy()
    quit(0)

  if answer == 1:
    wm.w_sprint("-- Entering global parameters", nl=True)
    wm.w_create(w_title="Global parameters")
    while True:
      menu_message = """
      1. Cluster settings
      2. Networks

      9. Go back

      """
      wm.w_sprint(textwrap.dedent(menu_message))
      answer = int(wm.w_input("❱❱❱ "))

      if answer == 9:
        break

      #######################################################################################################
      ###################### CLUSTER SETTINGS
      ########
      if answer == 1:

        wm.w_sprint("-- Entering cluster settings")
        wm.w_create(w_title="Cluster settings")
        # Basic configuration is in cluster.yml file
        # We open advanced configuration only if needed
        wm.w_sprint("-- Reading configuration")
        if os.path.exists("inventory/group_vars/all/cluster.yml"):
          with open("inventory/group_vars/all/cluster.yml", 'r') as file:
            cluster = yaml.safe_load(file)
        else:
          wm.w_sprint("-- Could not find file, generating default")
          cluster = {
            'bb_cluster_name' : 'bluebanquise-cluster',
            'bb_time_zone' : 'Europe/Brussels',
            'bb_domain_name' : 'cluster.local'
          }
        while True:
          menu_message = """
          1. Cluster name: {cna}
          2. Cluster Time zone: {ctz}
          3. Cluster domain name: {cdm}
          4. Advanced settings

          9. Go back

          """.format(
            cgreen=wm.w_allowed_colors['green'],
            creset=wm.w_allowed_colors['reset'],
            cna=wm.t_green(cluster['bb_cluster_name']),
            ctz=wm.t_green(cluster['bb_time_zone']),
            cdm=wm.t_green(cluster['bb_domain_name'])
          )
          wm.w_sprint(textwrap.dedent(menu_message))
          answer = int(wm.w_input("❱❱❱ "))

          if answer == 9:
            break

          if answer == 1:
            wm.w_sprint("Current cluster name is: " + wm.t_green(str(cluster['bb_cluster_name'])))
            wm.w_sprint("Please enter new name:")
            sub_answer = wm.w_input("❱❱❱ ")
            cluster['bb_cluster_name'] = sub_answer
            wm.w_sprint("-- Writting new configuration")
            with open("inventory/group_vars/all/cluster.yml", 'w+') as file:
              yaml.dump(cluster, file, default_flow_style=False)

          if answer == 2:
            wm.w_sprint("Current cluster time zone is: " + wm.t_green(str(cluster['bb_time_zone'])))
            wm.w_sprint("Please enter new time zone (enter nothing to display available time zones):")
            sub_answer = wm.w_input("❱❱❱ ")
            if sub_answer not in zoneinfo.available_timezones():
              wm.w_sprint('-- Time zone provided is not valid, please check syntax')
              wm.w_sprint('-- Available system time zones available are:')
              for tz in sorted(zoneinfo.available_timezones()):
                fprint(tz)
              continue
            cluster['bb_time_zone'] = sub_answer
            wm.w_sprint("-- Writting new configuration")
            with open("inventory/group_vars/all/cluster.yml", 'w+') as file:
              yaml.dump(cluster, file, default_flow_style=False)

          if answer == 3:
            wm.w_sprint("Current cluster domain name is: " + wm.t_green(str(cluster['bb_domain_name'])))
            wm.w_sprint("Please enter domain name:")
            sub_answer = wm.w_input("❱❱❱ ")
            if not validators.domain(sub_answer):
              wm.w_sprint('-- Domain name provided is not valid, please check syntax')
              continue
            cluster['bb_domain_name'] = sub_answer
            wm.w_sprint("-- Writting new configuration")
            with open("inventory/group_vars/all/cluster.yml", 'w+') as file:
              yaml.dump(cluster, file, default_flow_style=False)

          if answer == 4:
            wm.w_sprint("-- Reading advanced configuration")
            if os.path.exists("inventory/group_vars/all/cluster_advanced.yml"):
              with open("inventory/group_vars/all/cluster_advanced.yml", 'r') as file:
                cluster_advanced = yaml.safe_load(file)
            else:
              wm.w_sprint("-- Could not find file, generating default")
              cluster_advanced = {
                'bb_icebergs_system' : 'false'
              }
            wm.w_sprint(" ")
            for key, value in cluster_advanced.items():
              wm.w_sprint(wm.t_blue(str(key)) + ": " + str(value))
            wm.w_sprint(" ")
            wm.w_sprint("Please enter " + wm.t_blue("key") + " to edit")
            answer = wm.w_input("❱❱❱ ")
            if answer in cluster_advanced:
              wm.w_sprint("Ok, please enter now new value")
              sub_answer = wm.w_input("❱❱❱ ")
              cluster_advanced[answer] = sub_answer
              wm.w_sprint("-- Writting new configuration")
              with open("inventory/group_vars/all/cluster_advanced.yml", 'w+') as file:
                yaml.dump(cluster_advanced, file, default_flow_style=False)
            else:
              wm.w_sprint("-- Could not find key in list, please check entered syntax")
        wm.w_destroy()

      #######################################################################################################
      ###################### NETWORK SETTINGS
      ########
      if answer == 2:

        wm.w_sprint("-- Entering networks settings")
        wm.w_create(w_title="Network settings")
        wm.w_sprint("\n-- Reading configuration")
        if os.path.exists("inventory/group_vars/all/networks.yml"):
          with open("inventory/group_vars/all/networks.yml", 'r') as file:
            networks = yaml.safe_load(file)
        else:
          wm.w_sprint("-- Could not find file, generating default")
          networks = {
            'networks' : {}
          }
        while True:

          wm.w_sprint("Current configuration:")
          wm.w_sprint(" ")
          wm.w_sprint(yaml.dump(networks, default_flow_style=False))

          menu_message = """
          1. Add new network
          2. Edit existing network
          3. Delete network

          9. Go back

          """
          wm.w_sprint(textwrap.dedent(menu_message))
          answer = int(wm.w_input("❱❱❱ "))

          if answer == 9:
            break

          if answer == 1:
            wm.w_sprint("-- Entering new network")
            wm.w_create(w_title="New network")
            wm.w_sprint("\nPlease enter new network name:")
            wm.w_sprint("Remember that administration networks start with prefix " + wm.t_blue('net-') + '.')
            nname = wm.w_input("❱❱❱ ")
            networks['networks'][nname] = {}
            wm.w_sprint("Please enter network " + wm.t_blue(nname) + " subnet:")
            sub_answer = wm.w_input("❱❱❱ ")
            networks['networks'][nname]['subnet'] = sub_answer
            wm.w_sprint("Please enter network " + wm.t_blue(nname) + " prefix:")
            sub_answer = wm.w_input("❱❱❱ ")
            networks['networks'][nname]['prefix'] = sub_answer
            wm.w_sprint("Please enter network " + wm.t_blue(nname) + " gateway (ip4) if exist:")
            sub_answer = wm.w_input("❱❱❱ ")
            if sub_answer:
              networks['networks'][nname]['gateway4'] = sub_answer
            else:
              networks['networks'][nname]['gateway4'] = None
            if nname.startswith('net-'):
              wm.w_sprint("According to the name, this is an admininstration network.")
              wm.w_sprint("Register this network in dhcp server (Y/N)?")
              sub_answer = wm.w_input("❱❱❱ ")
              if sub_answer.lower() in ["y","yes"]:
                networks['networks'][nname]['dhcp_server'] = True
              else:
                networks['networks'][nname]['dhcp_server'] = False
              wm.w_sprint("Register this network in dns server (Y/N)?")
              sub_answer = wm.w_input("❱❱❱ ")
              if sub_answer.lower() in ["y","yes"]:
                networks['networks'][nname]['dns_server'] = True
              else:
                networks['networks'][nname]['dns_server'] = False
              wm.w_sprint("Should all services be on the same ip")
              wm.w_sprint("or do you plan to distribute services,")
              wm.w_sprint("like a dns server on another ip than time server?")
              wm.w_sprint("So question is: will this network use a single services ip? (Y/N)?")
              sub_answer = wm.w_input("❱❱❱ ")
              if sub_answer.lower() in ["y","yes"]:
                wm.w_sprint("Ok, using a global services ip for this network.")
                wm.w_sprint("What will be this ip?")
                sub_answer = wm.w_input("❱❱❱ ")
                networks['networks'][nname]['services_ip'] = sub_answer
              else:
                wm.w_sprint("Ok, generating default fine grained services.")
                wm.w_sprint("You will be able to define them or add others later.")
                networks['networks'][nname]['services'] = {}
                networks['networks'][nname]['services']['dns'] = []
                networks['networks'][nname]['services']['ntp'] = []
                networks['networks'][nname]['services']['pxe'] = []
            wm.w_sprint("-- Writting new configuration")
            with open("inventory/group_vars/all/networks.yml", 'w+') as file:
              yaml.dump(networks, file, default_flow_style=False)

          if answer == 2:
            wm.w_sprint("-- Entering network editor")
            wm.w_create(w_title="Network edit")
            wm.w_sprint("\nCurrent networks:")
            for net in networks['networks']:
              wm.w_sprint("- " + net)
            wm.w_sprint("Please enter network to edit:")
            nname = wm.w_input("❱❱❱ ")
            if not nname in networks['networks']:
              wm.w_sprint("Network unknown, please check syntax.")
              continue
            wm.w_sprint("Current network settings are:")
            wm.w_sprint(" ")
            for key, value in networks['networks'][nname].items():
              wm.w_sprint(wm.t_blue(str(key)) + ": " + str(value))
            wm.w_sprint(" ")
            wm.w_sprint("Please enter " + wm.t_blue("key") + " to edit")
            answer = wm.w_input("❱❱❱ ")
            if answer in networks['networks'][nname]:
              if answer == "services":
                wm.w_sprint("Current registered services:")
                for service, service_values in networks['networks'][nname]['services'].items():
                  wm.w_sprint(" - " + service + ": " + str(service_values))
                wm.w_sprint("Please select a service to edit")
                service = wm.w_input("❱❱❱ ")
                if service not in networks['networks'][nname]['services']:
                  wm.w_sprint("Service unknown, please check syntax.")
                  continue
                wm.w_sprint("You can add as multiple ipv4/hostname couples to each service.")
                wm.w_sprint("For now, you have to pass the dict as a string. For example:")
                wm.w_sprint("[{'ip4': '10.10.0.1', 'hostname': 'mgt1'},{'ip4': '10.10.0.2', 'hostname': 'mgt2'}]")
                wm.w_sprint("Please enter dict to set for this service:")
                answer = wm.w_input("❱❱❱ ")
                networks['networks'][nname]['services'][service] = json.loads(answer)
              else:
                wm.w_sprint("Ok, please enter now new value")
                sub_answer = wm.w_input("❱❱❱ ")
                networks['networks'][nname][answer] = sub_answer
              wm.w_sprint("-- Writting new configuration")
              with open("inventory/group_vars/all/networks.yml", 'w+') as file:
                yaml.dump(networks, file, default_flow_style=False)
            else:
              wm.w_sprint("-- Could not find key in list, please check entered syntax")

            wm.w_destroy()

        wm.w_destroy()

  if answer == 2:
    wm.w_sprint("-- Entering groups", nl=True)
    wm.w_create(w_title="Groups")
    while True:
      menu_message = """
      1. Cluster settings
      2. Networks

      9. Go back

      """
      wm.w_sprint(textwrap.dedent(menu_message))
      answer = int(wm.w_input("❱❱❱ "))

      if answer == 9:
        break

    wm.w_destroy()
