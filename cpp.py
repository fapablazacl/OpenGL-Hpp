
class Class:
    def __init__(self, name):
        self.name = name
        self.methods = []
    
    def generate(self):
        return """

class % {

};""" % (self.name)
