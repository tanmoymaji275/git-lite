class GitObject:
    def __init__(self, data=None):
        if data is not None:
            self.deserialize(data)
        else:
            self.init()
 
    def serialize(self):
        raise NotImplementedError
 
    def deserialize(self, data):
        raise NotImplementedError
 
    def init(self):
        pass