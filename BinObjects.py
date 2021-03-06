
class BinObject(object):
    def __init__(self, in_path):
        self.path = in_path
        self.data = open(in_path, "rb").read()

    def __repr__(self):
        x = "input: " + str(self.path)
        return x


class BinaryList(object):
    def __init__(self, input_path, logger=None):
        from glob import glob
        from os.path import join
        self.logger = logger
        pathlist = glob(join(input_path,'*.bin'))

        self.list = [BinObject(pathlist.pop()) for i in xrange(len(pathlist))]

        # print (instancelist)
    def pop(self):
        retobj = self.list.pop(0)
        if self.logger is not None:
            self.logger.debug("BinaryList.get:: Returned value: %r", retobj.path)
        return retobj

    def peek(self, i=0):
        retobj = self.list[i]
        if self.logger is not None:
            self.logger.debug("BinaryList.peek:: Returned value: %r", retobj.path)
        return retobj

