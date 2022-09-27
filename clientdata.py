import requests

class clientdata(object):
    client = None
    allotnum = None
    allotmaxnum = None

    def __init__(self, allotnum : int = 0, allotmaxnum : int = 3):
        self.allotnum = allotnum
        self.allotmaxnum = allotmaxnum
        self.client = requests.Session()