
class BinObject(object):
    def __init__(self, path):
        self.path = path
        self.data = open(path, "rb").read()

    def __repr__(self):
        x = "input: " + str(self.path)
        return x


class BinaryList(object):
    def __init__(self, input_path, output_path):
        from glob import glob
        from os.path import join

        pathlist = glob(join(input_path,'*.bin'))
        self.list = [BinObject(pathlist.pop()) for i in xrange(len(pathlist))]

        #print (instancelist)