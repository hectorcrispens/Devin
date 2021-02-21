import os
import json
from collections import namedtuple
from smdt import *
import time

class RollItem():
    def __init__(self, path, section, block, op, value, chain):
        self.path = path
        self.section = section
        self.block = block
        self.op = op
        self.value = value
        self.chain = chain
        
class Rollback():
    
    place = os.path.dirname(__file__)
    
    @classmethod    
    def load(self):
        stack = None
        try:
            with open(os.path.join(Rollback.place, "stack.json"), "r") as f:
                text = f.read()
                stack = json.loads(text)
                return stack
        except IOError:
            f = open(os.path.join(Rollback.place, "stack.json"), "w")
            f.write("{ \"stack\": [] }")
            f.close()
            return self.load()

    @classmethod
    def save(self, obj):
        text = json.dumps(obj, indent=4)
        #print(os.path.join(Rollback.place, "stack.json"))
        with open(os.path.join(Rollback.place, "stack.json"), "w") as f:
            f.write(text)

    @classmethod
    def push(self, value):
        stack = self.load()
        stack["stack"].append(value.__dict__)
        self.save(stack)

    @classmethod
    def chain(self):
        try:
            lista = [self.pop()]
            if not lista[0]:
                return lista[0]
            item = self.floop()
            while item and item.chain == lista[0].chain:
                item = self.pop()
                lista.append(item)
                item = self.floop()
            return lista
        except AttributeError:
            print("Error in the chain read")
            return None

    @classmethod
    def floop(self):
        stack = self.load()
        try:
            item = stack["stack"][-1]
            self.save(stack)
            #print(type(item))
            named = namedtuple("RollItem", item.keys())(*item.values())
            #self.imprime(named)
            return named
        except IndexError:
            print("El Stack se ha vaciado")
    
        
    @classmethod
    def pop(self):
        stack = self.load()
        try:
            item = stack["stack"].pop(-1)
            self.save(stack)
            #print(type(item))
            named = namedtuple("RollItem", item.keys())(*item.values())
            #self.imprime(named)
            return named
        except IndexError:
            print("El Stack se ha vaciado")

    @classmethod
    def imprime(self, named):
        #print("-------------------")
        print("section: "+str(named.section))
        print("value: "+named.value)
        print("path: "+named.path)
        print("block: "+str(named.block))
        print("operation: " +named.op)
        print("chain: "+named.chain)

    @classmethod
    def start(self):
        t = ""
        t=t + "from Context import *\n"
        t=t + "from Engine import Engine\n"
        t=t + "import os\n"
        t=t + "class Start():\n"
        t=t + "    modules = {\n"
        modules = self.openModules()
        for x in modules["modules"]:
            t=t + "        \"" + x["nombre"] + "\" : "+ x["clase"] +"(),\n"
        t=t + "        \"Engine\" : Engine()\n"
        t=t + "        }\n"
        t=t + "    def getM(self):\n"
        t=t + "        return self.modules\n"

        f = open(os.path.join(self.place,"start.py"), "w")
        f.write(t)
        f.close()

    @classmethod
    def openModules(self):
        f = open(os.path.join(self.place ,"modules.json"), "r")
        modulesString = f.read()
        modules = json.loads(modulesString)
        f.close()
        return modules
        
        
    @classmethod
    def revert(self):
        chain = self.chain()
        if chain:
            print("Rollback changes...")
            time.sleep(5)
            for n in chain:
                #self.imprime(n)
                if "Functions.py" in n.path:
                    #print("in function.py")
                    parsed = Smdt.parse(n.path)
                    if n.op == "push":
                        parsed.push(n.section, n.value)
                    if n.op == "pop":
                        s, i = parsed.find(n.value)
                        if s or i:
                            parsed.pop(s, i)
                    Smdt.persist(n.path, parsed)
                if "modules.json" in n.path:
                    #print("in modules.json")
                    f = open(n.path, "r")
                    text = f.read()
                    f.close()
                    mod = json.loads(text)
                    if n.op == "push":
                        value = json.loads(n.value)
                        mod[n.section].append(value)
                    if n.op == "pop":
                        if n.section == "functions":
                            lam = lambda x : mod["functions"].remove(x)
                            l = lambda x : x["name"] == n.value
                            lista = filter(l,  mod["functions"])
                            map(lam, lista)
                        if n.section == "modules":
                            idx = 0
                            for x in mod["modules"]:
                                if x["nombre"] == n.value:
                                    del mod["modules"][idx]
                            else:
                                idx+=1
                    g = open(n.path, "w")
                    text = json.dumps(mod, indent=4)
                    g.write(text)
                    g.close()
                if "Context.py" in n.path:
                    parsed = Smdt.parse(n.path)
                    if n.op == "push":
                        parsed.push(n.section, n.value)
                    if n.op == "pop":
                        parsed.pop(n.section, n.block)
                    Smdt.persist(n.path, parsed)
            self.start()
            print("done")
            
