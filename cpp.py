
class Class:
    def __init__(self, name):
        self.name = name
    
    def generate(self):
        return """
class % {

};""" % (self.name)
