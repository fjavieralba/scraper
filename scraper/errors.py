#coding: utf-8

class RequestPageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IndexError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)