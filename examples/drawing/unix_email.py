#!/usr/bin/env python
"""
Create a directed graph, allowing multiple edges and self loops, from
a unix mailbox.  The nodes are email addresses with links
that point from the sender to the recievers.  The edge data
is a Python email.Message object which contains all of
the email message data.

This example shows the power of XDiGraph to hold edge data
of arbitrary Python objects (in this case a list of email messages).

By default, load the sample unix email mailbox called "unix_email.mbox".
You can load your own mailbox by naming it on the command line, eg

python unixemail.py /var/spool/mail/username

"""
# Author: Aric Hagberg (hagberg@lanl.gov)

#    Copyright (C) 2005-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import email
from email.utils import getaddresses,parseaddr
import mailbox
import sys

# unix mailbox recipe
# see http://www.python.org/doc/current/lib/module-mailbox.html
def msgfactory(fp):
    try:
        return email.message_from_file(fp)
    except email.Errors.MessageParseError:
        # Don't return None since that will stop the mailbox iterator
        return ''



if __name__ == '__main__':

    import networkx as nx
    try:
        import matplotlib.pyplot as plt
    except:
        pass

    if len(sys.argv)==1:
        filePath = "unix_email.mbox"
    else:
        filePath = sys.argv[1]

    mbox = mailbox.mbox(filePath, msgfactory) # parse unix mailbox

    G=nx.MultiDiGraph() # create empty graph

    # parse each messages and build graph
    for msg in mbox: # msg is python email.Message.Message object
        (source_name,source_addr) = parseaddr(msg['From']) # sender
        # get all recipients
        # see http://www.python.org/doc/current/lib/module-email.Utils.html
        tos = msg.get_all('to', [])
        ccs = msg.get_all('cc', [])
        resent_tos = msg.get_all('resent-to', [])
        resent_ccs = msg.get_all('resent-cc', [])
        all_recipients = getaddresses(tos + ccs + resent_tos + resent_ccs)
        # now add the edges for this mail message
        for (target_name,target_addr) in all_recipients:
            G.add_edge(source_addr,target_addr,message=msg)

    # print edges with message subject
    for (u,v,d) in G.edges_iter(data=True):
        print("From: %s To: %s Subject: %s"%(u,v,d['message']["Subject"]))


    try: # draw
        pos=nx.spring_layout(G,iterations=10)
        nx.draw(G,pos,node_size=0,alpha=0.4,edge_color='r',font_size=16)
        plt.savefig("unix_email.png")
        plt.show()
    except: # matplotlib not available
        pass
