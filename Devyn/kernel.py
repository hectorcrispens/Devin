# -*- coding: utf-8 -*-
import json
import optparse
import os
from Lib.start import Start
from Lib.modulo import Modulo
class Kernel():
        
        def __init__(self, config):
                self.work = os.getcwd() + "/"
                self.place = os.path.dirname(__file__) #<-- absolute dir the script is in
                self.local = config + "/Config/"
                #print(self.local)
                #abs_file_path = os.path.join(script_dir, rel_path)
                #/home/hector/.Devyn

                
        def proyectar(self, sigma, pares, S, N ):
                if not sigma or not pares:
                        return
                else:
                        proy=lambda y : y in pares[0][1]
                        clavesin = filter(proy, sigma)
                        if clavesin:
                                for p in clavesin:
                                        N[pares[0][0]]((p,S[p]))
                                        removed = list(set(sigma)-set(clavesin))
                                self.proyectar(removed, pares[1:], S, N)
                        else:
                                self.proyectar(sigma, pares[1:], S, N)


        def N(self):
                p = Start()
                return  p.getM()
                
        def openModules(self):
                filename = os.path.join(self.place , "Lib/modules.json")
                try:
                    with open(filename, "r") as f:
                        modulesString = f.read()
                        modules = json.loads(modulesString)
                        f.close()
                        return modules
                except IOError:
                        h = open(filename, "w")
                        h.write("{ \"functions\": [], \"modules\": [] }")
                        h.close()
                        return self.openModules()

        def saveModules(self, modules):
                # Guardamos el contenido en modules.json
                f = open(os.path.join(self.local , "modules.json"), "w")
                modulesString = json.dumps(modules, indent=4)
                f.write(modulesString)
                f.close()

        def openKModules(self):
                mod = Modulo()
                modules = mod.get()
                return modules        


        def pares(self):
                modulesK = self.openKModules()
                tree = []
                for h in modulesK["comandos"]:
                        tree.append(h["dest"])
                modules = self.openModules()
                lista =[]
                lista.append(("Engine", tree))
                for x in modules["modules"]:
                        config = x["config"]
                        c = []
                        for y in config["comandos"]:
                                c.append(y["dest"])
                        lista.append((x["nombre"],c))
                return lista
        

        #Agrega todos los comandos del kernel al parser
        def inicializeParser(self, parser):
                dic = self.openKModules()
                group = optparse.OptionGroup(parser, dic["groupDescripcion"])
                self.mapper(dic, group)
                parser.add_option_group(group)

        def inject(self, parser):
                modules = self.openModules()
                for n in modules["modules"]:
                        config = n["config"]
                        group = optparse.OptionGroup(parser, config["groupDescripcion"])
                        self.mapper(config, group)
                        parser.add_option_group(group)

        def mapper(self, dic, group):
                for x in dic["comandos"]:
                        x.setdefault("help", "")
                        x.setdefault("nargs", 0)
                        p = lambda x : str(x)
                        x["command"].append("")
                        x["command"] = map(p, x["command"])
                        if "type" in x and x["action"] not in  ["store_true", "store_false"]:
                                x.setdefault("default", None)
                                group.add_option(
                                        x["command"][0],
                                        x["command"][1],
                                        help=x["help"],
                                        type=str(x["type"]),
                                        nargs=x["nargs"],
                                        action=str(x["action"]),
                                        default=str(x["default"]),
                                        dest=str(x["dest"])
                                )
                        else:
                                x.setdefault("default", False)
                                group.add_option(
                                        x["command"][0],
                                        x["command"][1],
                                        help=x["help"],
                                        default=False,
                                        action=str(x["action"]),
                                        dest=str(x["dest"])
                                )

        

                        
