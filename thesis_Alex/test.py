import graphs as g

if __name__ == '__main__':
    g_1 = g.g_1()
    print(g_1.nodes())

    g_1.remove_edge('6', '7')
    print(g_1.nodes())



