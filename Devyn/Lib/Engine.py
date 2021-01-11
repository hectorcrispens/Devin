# -*- coding: utf-8 -*-
import os
import json
import re
import math
import ast, traceback
from Funciones.ApiContext import ApiContext
from Funciones.Functions import *
from Colores import Color
from modulo import Modulo
from Rollback import Rollback, RollItem
from smdt import Smdt, ObjSmdt

class Engine(ApiContext):
    debug = False
    def __init__(self):
        self.args= None
        self.work = os.getcwd() + "/"
        self.place = os.path.dirname(__file__) #<-- absolute dir the script is in
        #abs_file_path = os.path.join(script_dir, rel_path)
        #self.apiHello("axdModule")
        #functionHello("axdModuleFunctions")
        #f = open(os.path.join(self.place ,"modules.json"), "r")

    def __call__(self, args):
        if args[0]=="template":
            self.template(args[1])
        if args[0]=="install":
            if self.checkmod(args[1]):
                self.install(args[1])
            else:
                print(Color.RED+"No se pudo encontrar los archivos necesarios para instalar un Modulo"+ Color.END)
                
        if args[0]=="uninstall":
            self.uninstall(args[1])
            
        if args[0]=="add":
           value = re.sub('\.py', '', args[1])
           filename = os.getcwd() +"/"+ value +".py"
           l = lambda x : "ñ" in x
           if self.check(filename):
               proh = filter(l, self.funUsr(filename))
               if not proh:
                   self.add(value)
               else:
                   print(" las siguientes funciones no estan permitidas ", proh)
                
           else:
              print(Color.RED+"No se pudo encontrar un archivo de funciones de Python"+ Color.END)
              
        if args[0]=="delete":
            self.delete(args[1])
        if args[0]=="summary":
            self.summary(args[1])

        if args[0]=="test":
            self.test(args[1])

    def test(self, value):
        chain = Rollback.chain()
        if chain:
            for n in chain:
                Rollback.imprime(n)
                if "Functions.py" in n.path:
                    print("in function.py")
                    parsed = Smdt.parse(n.path)
                    if n.op == "push":
                        parsed.push(n.section, n.value)
                    if n.op == "pop":
                        s, i = parsed.find(n.value)
                        if s or i:
                            parsed.pop(s, i)
                    Smdt.persist(n.path, parsed)
                if "modules.json" in n.path:
                    print("in modules.json")
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
            
        # parsed = Smdt.parse(os.path.join(self.place,"Funciones/Functions.py"))
        # x, i = parsed.find(value)
        # print(x, i)
        
        #def{1}.*\n+.*\n?
        # filename = os.getcwd() +"/"+ value +".py"
        # try:
        #     f = open(filename, "r")
        #     text = f.read()
        #     text = re.sub(r"#.*\n", "", text)
        #     f.close()
        #     h = re.split(r"def", text)[1:]
        #     for n in h:
        #         print("----------------------------------")
        #         print("def"+n)
        # except IOError:
        #     print("eeror de lectura")

    def checkmod(self, name):
        filename = os.getcwd() +"/"+ name +"/"+name +".json"
        if self.check(filename):
             mod = self.modUsr(name)
             filenpy = os.getcwd() +"/"+ name +"/"+mod["archivo"] +".py"
             if self.check(filenpy):
                 return True
             else:
                 return False
        else:
            return False
        
    def check(self, filename):
        try:
            with open(filename, "r") as f:
                f.close()
                return True
        except IOError:
            return False
        
        
    def summary(self, value):
        w = 75
        H = lambda s, n : "".join([" "]*(n-len(s)))
        modules = self.openModules()
        for x in modules["functions"]:
            if len(x["text"]) > (w-17):
                w = len(x["text"]) + 17
        print(Color.HEADER + "+"+"="*(w-2)+"+" + Color.END)
        floor = int(math.floor(((w-11)/2)))
        print(Color.HEADER+"|"+Color.END+" "*floor+Color.BOLD+"FUNCIONES"+Color.END +" "*(w-(11+floor))+ Color.HEADER+"|")
        print("+"+"="*(w-2)+"+" + Color.END)
        for x in modules["functions"]:
            key = x["name"]
            valor = x["text"]
            arg = x["args"]
            print(Color.HEADER +"|"+Color.GREEN+" -> "+Color.END + str(key)+":" + H(key, (w-7)) +Color.HEADER+ "|")
            print("|               "+Color.RED +"["+Color.END+ str(arg)+Color.RED+"]" + H(arg, (w-19)) +Color.HEADER+ "|")
            print("|               "+Color.END + str(valor) + H(valor, (w-17)) +Color.HEADER+ "|"+ Color.END)
        print(Color.HEADER +"+"+"="*(w-2)+"+")
        floor = int(math.floor((w-9)/2))
        print("|"+Color.END+Color.BOLD+" "*floor+"MODULOS"+" "*(w-(9+floor))+Color.HEADER+"|")
        print("+"+"="*(w-2)+"+")
        for x in modules["modules"]:
            print("|"+Color.RED+"__ "+Color.END+"Modulo: " + str(x["nombre"]) + H(x["nombre"],(w-13)) +Color.HEADER +"|")
            config = x["config"]
            for n in config["comandos"]:
                print("|"+Color.BLUE+"______________"+Color.END + n["dest"] + H(n["dest"], (w-16)) +Color.HEADER +"|")
        print("+"+"="*(w-2)+"+"+ Color.END)

    def delete(self, name):
        filename = os.getcwd() + "/" + name + ".py"
        mod = self.openModules()
        lam = lambda x : mod["functions"].remove(x)
        rollam = lambda x : Rollback.push(RollItem(os.path.join(self.place ,"modules.json"), "functions", 0, "push", json.dumps(x), "remove"))
        try:
            with open(filename, "r") as f:
                funciones = self.funUsr(filename)
                l = lambda x : x["name"] in funciones
                lista = filter(l,  mod["functions"])
                map(rollam, lista)
                #lista tiene todaaas las funciones que hay que apilar
                map(lam, lista)
                self.saveModules(mod)
                self.remove(funciones)
        except IOError:
            funciones = [name]
            l = lambda x : x["name"] in funciones
            lista = filter(l,  mod["functions"])
            map(rollam, lista)
            map(lam, lista)
            self.saveModules(mod)
            self.remove(funciones)

    def remove(self, lista):
        self.spread("lista -> ",lista)
        path = os.path.join(self.place,"Funciones/Functions.py")
        parsed = Smdt.parse(path)
        for item in lista:
            x, i = parsed.find(item)
            self.spread("item -> ", item)
            self.spread("x ->", x)
            self.spread("i -> ", i)
            if x  or i :
                value = parsed.pop(x, i)
                self.spread("value in pop -> ", value)
                rol = RollItem(path, x, i, "push", value, "remove")
                Rollback.push(rol)
        Smdt.persist(path, parsed)
            
        # g = open(os.path.join(self.place,"Funciones/Functions.py"), "r")
        # text = g.read()
        # g.close()
        # f = open(os.path.join(self.place ,"Funciones/Functions.py"), "w")
        # p = text.split("def ")
        # for h in p[1:]:
        #     name = h.split("(")[0]
        #     if name not in lista:
        #         f.write("def " + h)
        #     #Hay que acumular todas las funciones en una lista
        #    #else:
        #    #    Rollback.push("def " + h)
        # f.close()


        
            
    def spread(self, key, value):
        if self.debug:
            print(key, value)
            
    def add(self, name):
        filename = os.getcwd() +"/"+ name +".py"
        dictionario = self.comUsr(filename)
        claves = self.funUsr(filename)
        arguments = self.argUsr(filename)
        modules = self.openModules()
        self.spread("[145]Functions -->",  modules["functions"])
        clavesmod = []
        for gg in modules["functions"]:
            clavesmod.append(gg["name"])
        l = lambda x: x in clavesmod
        carry = filter(l, claves)
        self.spread("[149]Claves -->", claves)
        self.spread("[150]Claves en modules -->", clavesmod)
        self.spread("[151]Carry -->", carry)
        if not carry and self.checker(filename):
            self.appendf(filename)
            only = filter(lambda x : x not in dictionario.keys(), claves)
            for n in dictionario.keys():
                modules["functions"].append({"name": n, "text": dictionario[n], "args": arguments[n]})
                rol = RollItem(os.path.join(self.place ,"modules.json"), "functions", 0, "pop", n, "add")
                Rollback.push(rol)
            for j in only:
                modules["functions"].append({"name":j, "text":" ", "args": arguments[j]})
                rol = RollItem(os.path.join(self.place ,"modules.json"), "functions", 0, "pop", j, "add")
                Rollback.push(rol)
            #modules["functions"] = modules["functions"] + funciones
            self.saveModules(modules)
            
    # def appendf(self, filename):
    #     f = open(filename, "r")
    #     g = open(os.path.join(self.place,"Funciones/Functions.py"), "a")
    #     for n in f:
    #         if not re.match('#@.*\n', n):
    #             g.write(n + "\n")
    #     f.close()
    #     g.close()
    def appendf(self, filename):
        f = open(filename, "r")
        value = f.read()
        value = re.sub(r"#.*\n", "", value)
        f.close()
        value = re.split(r"def", value)[1:]
        path = os.path.join(self.place,"Funciones/Functions.py")
        parsed = Smdt.parse(path)
        for n in value:
            (s, i) = parsed.push(0, "def" + n)
            rol = RollItem(path, s, i, "pop","", "add")
            Rollback.push(rol)
        Smdt.persist(path,parsed)
        

    def funUsr(self, filename):
        f = open(filename, "r")
        claves = []
        for x in f:
           if re.match('def\s[a-z]+', x):
               y = x.replace("def ","")
               segment = y.split("(")
               claves.append(segment[0])
        f.close()
        return claves
    
    def argUsr(self, filename):
        f = open(filename, "r")
        claves = {}
        for x in f:
           if re.match('def\s[a-z]+', x):
               y = x.replace("def ","")
               segment = y.split("(")
               claves[segment[0]] = segment[1].split(")")[0]
        f.close()
        return claves
    
    def comUsr(self, filename):
        f = open(filename, "r")
        text = f.read()
        tokens = re.findall("#@.*\n.*\(", text)
        l = lambda x : re.sub('\n.*def','#@',x.replace("(","")).split("#@")
        n =map(l,tokens)
        lista={}
        for s in n:
            lista[s[2].replace(" ", "")] = s[1]
        return lista

    def checker(self, filename):
        with open(filename, "r") as f:
            source = f.read()
            valid = True
        try:
            ast.parse(source)
        except SyntaxError:
            valid = False
            traceback.print_exc()  # Remove to silence any errros
        return valid

    def uninstall(self, name):
        modules = self.openModules()
        idx = 0
        for x in modules["modules"]:
            if x["nombre"] == name:
                item = modules["modules"][idx]
                del modules["modules"][idx]
                rol = RollItem(os.path.join(self.place ,"modules.json"), "modules", 0, "push", json.dumps(item), "uninstall")
                Rollback.push(rol)
            else:
                idx+=1
        self.saveModules(modules)
        self.start()
        self.delContext(name)
        

    def install(self, name):
        matriz = self.matriz()
        fila = self.filaUsr(name)
        carry = []
        self.filamatriz(fila, matriz, carry)
        mod = self.modUsr(name)
        filename = os.getcwd() +"/"+ name +"/"+mod["archivo"] +".py"
        if not carry and self.checker(filename):
            mu = self.modUsr(name)
            modulos = self.openModules()
            modulos["modules"].append(mu)
            rol = RollItem(os.path.join(self.place ,"modules.json"), "modules", 0, "pop", name, "install")
            Rollback.push(rol)
            self.saveModules(modulos)
            self.appendC(name)
            self.start()
        else:
            print("Hay un inconveniente en el modulo cerca de " , carry)
            

        
    def itemitem(self, item1, item2):
        l = lambda x : x in item2[1]
        rest = filter(l, item1[1])
        if item1[0] != item2[0] and not rest:
            return False
        else:
            return True

    def itemfila(self, item, fila):
        l = lambda x: self.itemitem(item, x)
        ret = filter(l, fila[1])
        if not ret:
            return False
        else:
            return True
        
    def filafila(self, fila1, fila2, carry):
        l = lambda n : self.itemfila(n, fila2)
        x = filter(l, fila1[1])
        carry += x

    def filamatriz(self, fila, matriz, carry):
        if not matriz:
            return carry
        else:
            self.filafila(fila, matriz[0], carry)
            return self.filamatriz(fila, matriz[1:], carry)
    
    def modUsr(self, name):
        try:
            with open(os.getcwd() +"/"+ name +"/"+name +".json", "r") as f:
                text = f.read()
                mod = json.loads(text)
                f.close()
                return mod
        except IOError:
            return None
        
    def appendC(self, name):
        mod = self.modUsr(name)
        pathUser= os.getcwd() +"/"+ name +"/"+mod["archivo"] +".py"
        path = os.path.join(self.place,"Context.py")                    
        bimp, bbody = Smdt.extract(pathUser, name)
        parsed = Smdt.parse(path)
        (s, i)=parsed.push(0, bimp)
        (s2, i2)=parsed.push(1, bbody)
        Smdt.persist(path,parsed)
        rol = RollItem(path, s, i, "pop", name, "install" )
        rol2 = RollItem(path, s2, i2, "pop", name, "install")
        Rollback.push(rol)
        Rollback.push(rol2)
        
        
    def append(self, context):
        t = open(os.path.join(self.place,"Context.py"), "a")
        t.write("#--\n")
        t.write(context + "\n")
        t.close()

    def context(self):
        f = open(os.path.join(self.place ,"Context.py"), "r")
        text = f.read()
        f.close()
        return text
    
    def delContext(self, name):
        path = os.path.join(self.place,"Context.py")
        context = Smdt.parse(path)
        s, i = context.find(name)
        while s and i:
            value = context.pop(s,i)
            rol = RollItem(path, s, i, "push", value, "uninstall")
            Rollback.push(rol)
            s, i = context.find(name)
        Smdt.persist(path, context)
        #text = self.context()
        #g = open(os.path.join(self.place,"Context.py"), "w")
        #lista = text.split("#--\n")
        #g.write(lista[0])
        #g.close()
        #for n in lista[1:]:
        #    if name not in n:
        #        self.append(n)

    def imports(self):
        mod =  self.openModules()
        print(self.context().split("#@--"))


    def filaUsr(self, name):
        md = self.modUsr(name)
        cf = md["config"]
        fila = [md["nombre"]]
        cmd = []
        for x in cf["comandos"]:
            cmd.append(self.celda(x))
        fila.append(cmd)
        return fila
    
    def matriz(self):
        kernel = self.openKernel()
        filaP = ["Engine"]
        fila = []
        matriz= []
        for n in kernel["comandos"]:
            fila.append(self.celda(n))
        filaP.append(fila)
        matriz.append(filaP)
        modules = self.openModules()
        for p in modules["modules"]:
            filaT =[p["nombre"]]
            filax = []
            config = p["config"]
            for h in config["comandos"]:
                filax.append(self.celda(h))
            filaT.append(filax)
            matriz.append(filaT)
        return matriz

    def template(self, name):
        chapter = name + "Module"
        os.mkdir(chapter)
        template = {
            "nombre": name + "Module",
            "clase": name.title() + "ModuleClass",
            "archivo": name + "ModuleFile",
            "config" : {
                "groupDescripcion":"user Descriptions",
                "imports":[("Datetime", "TimeDelta"), ("json")],
                "comandos": [
                    {
                        "command" : ['--hello'],
                        "action" : "store_true",
                        "default" : "False",
                        "help" : "Hello World!!!",
                        "dest" : "hello",
                        "nargs" : 2,
                        "type": "string"
                    }
                ]
            }
        }
        f = open(chapter + "/" + name +"Module.json", "w")
        text = json.dumps(template, indent=4)
        f.write(text)
        f.close()
        destino = open(chapter + "/" + name + "ModuleFile.py", "w")
        destino.write("class "+ name.title() +"ModuleClass(ApiContext):\n")
        destino.write("    def __init__(self):\n")
        destino.write("        self.args= None\n")
        destino.write("\n")    
        destino.write("    def __call__(self, args):\n")
        destino.write("        self.apiArgs(self.args)\n")
        destino.write("        if args[0] == \"hello\":\n")
        destino.write("            self.hello(args[1])\n")
        destino.write("\n")
        destino.write("    def hello(self, name):\n")
        destino.write("        print(\"hello world \", + name)\n")
        destino.write("        self.apiHello(\""+name+"Module\")\n")
        destino.write("        functionHello(\""+name+"ModuleFunctions\")\n")

        destino.close()

    def openKernel(self):
        mod = Modulo()
        return mod.get()
    
    def openModules(self):
        f = open(os.path.join(self.place ,"modules.json"), "r")
        modulesString = f.read()
        modules = json.loads(modulesString)
        f.close()
        return modules
    
    def saveModules(self, modules):
        # Guardamos el contenido en modules.json
        f = open(os.path.join(self.place,"modules.json"), "w")
        modulesString = json.dumps(modules, indent=4)
        f.write(modulesString)
        f.close()
                         
    def celda(self, comando):
        return [comando["dest"], tuple(comando["command"])]
                        
        
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
