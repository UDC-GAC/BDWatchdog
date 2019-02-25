import pickle

process_files = ["NameNode", "SecondaryNameNode", "DataNode", "ResourceManager", "NodeManager", "YarnChild",
                 "MRAppMaster"]
for f in process_files:
    try:
        with open('../pipelines/java_mappings/' + f + '.txt', 'rb') as fp:
            itemlist = pickle.load(fp)
        print(f + "->" + str([int(x) for x in itemlist]))
    except IOError:
        pass
