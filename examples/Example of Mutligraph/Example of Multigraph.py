#!/usr/bin/env python
# coding: utf-8

# In[1]:


import networkx as nx


# In[46]:


MG_1 = nx.MultiGraph()


# In[47]:


L=[1,2,3]
MG_1.add_nodes_from(L)
MG_1.add_edges_from([("FOUR", 5), (5, 6)], color='red')
MG_1.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 9}),(1,6),("FOUR",3)])


# In[48]:


nx.to_numpy_array(MG_1,dtype= int)

