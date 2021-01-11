# -*- coding: utf-8 -*-

#@imports
#-
from Funciones.ApiContext import ApiContext
#@modules
#-
class TitoModuleClass(ApiContext):
    def __init__(self):
        self.args= None

    def __call__(self, args):
        self.apiArgs(self.args)
        if args[0] == "hello":
            self.hello(args[1])

    def hello(self, name):
        print("hello world ", + name)
        self.apiHello("titoModule")
        functionHello("titoModuleFunctions")
#-
class TitoModuleClass(ApiContext):
    def __init__(self):
        self.args= None

    def __call__(self, args):
        self.apiArgs(self.args)
        if args[0] == "hello":
            self.hello(args[1])

    def hello(self, name):
        print("hello world ", + name)
        self.apiHello("titoModule")
        functionHello("titoModuleFunctions")
