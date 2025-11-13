#!/bin/sh
# From https://serverfault.com/questions/152795/linux-command-to-wait-for-a-ssh-server-to-be-up

echo "Trying to join $1 over ssh..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 echo hello
while test $? -gt 0
do
   sleep 5 # highly recommended - if it's in your local network, it can try an awful lot pretty quick...
   echo "Trying again..."
   ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 echo hello
done
