#!/usr/bin/env python
"""
Create a directed graph, allowing multiple edges and self loops, from
a unix mailbox.  The nodes are email addresses with links
that point from the sender to the recievers.  The edge data
is a Python email.Message object which contains all of
the email message data. 

This example shows the power of XDiGraph to hold edge data
of arbitrary Python objects (in this case a list of email messages).

By default, load the sample unix email mailbox called "sample.mbox".
You can load your own mailbox by naming it on the command line, eg

python unixemail.py /var/spool/mail/username

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-03-22 13:57:46 -0700 (Tue, 22 Mar 2005) $"
__credits__ = """"""
#    Copyright (C) 2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import email
from email.Utils import getaddresses,parseaddr
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

    import networkx as NX
    try: 
        import pylab as P
    except:
        pass

    if len(sys.argv)==1:
        file="sample.mbox"
    else:
        file=sys.argv[1]
    fp=open(file,"r")

    mbox = mailbox.UnixMailbox(fp, msgfactory) # parse unix mailbox

    G=NX.MultiDiGraph() # create empty graph

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
            G.add_edge(source_addr,target_addr,msg)  

    # print edges with message subject
    for (u,v,m) in G.edges_iter(data=True):
        print "From: %s To: %s Subject: %s"%(u,v,m["Subject"])
    

    try: # draw
        pos=NX.spring_layout(G,iterations=10)
        NX.draw(G,pos,node_size=2000,alpha=0.5)
        P.show()
    except: # matplotlib not available
        pass
