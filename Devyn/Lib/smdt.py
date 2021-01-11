import re
class ObjSmdt():
    def __init__(self):
        self.non = None
        self.form = {}
        
    def pop(self, s, b):
        key = s
        try:
            if isinstance(s, int) and s < len(self.form.keys()):
                key= self.form.keys()[s]
            value = self.form[key][b]
            self.form[key].remove(value)
            return value
        except IndexError, KeyError:
            return None

    def push(self, s, value):
        key = s
        try:
            if isinstance(s, int) and s < len(self.form.keys()):
                key = self.form.keys()[s]
            self.form[key].append(value)
            return (key, len(self.form[key])-1)
        except IndexError:
            print(IndexError)
        
    def find(self, reg):
        for x, y in self.form.items():
             index = 0
             for n in y:
                 if reg in n:
                     return (x, index)
                 index+=1
        return None, None
        
        

        
class Smdt():
	first={"py":"#", "php":"/*","html":"<!--"}
	last={"py":"\n", "php":"\n","html":"\n"}
	stag="#@"
	btag="#-"
        nstag = "#@[a-z0-9]*\s*\n"
        nbtag = "#-"
        nsub ="[#@\s\n]"

        # ESTAS SE USAN PARA EXTRAER LOS imports
        reg='import\s[a-zA-Z]+(\s(as)?\s[a-zA-Z]+)?'
	fro = 'from\s[a-zA-Z]+\s'
        xp = '(import|from).*\n'
        # exp="#-[->](\[[a-z]+\])?\s*\n"
        #fullexp="\(([a-z]+=([a-z]+|[0-9]+),\s*)*\s*[a-z]+=([a-z]+|[0-9]+)\)"

        @classmethod
        def extract(self, path, name):
            with open(path, "r") as f:
	        body = f.read()
                block ="#("+name+")\n"
	        iter = re.finditer(Smdt.xp,body)
                for x in iter:
                    block+=x.group()
                return block, "class"+body.split("class")[1]
	#for x in block:
		#print(x.group())

        @classmethod
	def sopen(self, path):
	    try:
		f = open(path, "r")
		text = f.read()
		f.close()
		return text
	    except IOError:
		print("Error al abrir el archivo")
		exit()
	@classmethod
	def section(self, path):
	    parsed = Smdt.parse(path)
	    ext = path.split(".")[-1]
	    parsed.append([""])
	    Smdt.persist(path, parsed)

        @classmethod
        def parse(self, path):
            ob = ObjSmdt()
            f = Smdt.sopen(path)
            result = re.split(Smdt.nstag, f)
            claves = re.findall(Smdt.nstag, f)
            non=None
            if len(claves) == (len(result)-1):
                non = result[0]
                result = result[1:]
            claves= list(map(lambda x: re.sub(Smdt.nsub, "", x), claves))
            result = list(map(lambda x : re.split(Smdt.nbtag, x)[1:], result))
            if len(claves) == len(result):
                ob.non = non
                for j in range(len(claves)):
                    ob.form[claves[j]] = result[j]
            return ob
                

        @classmethod	
	def persist(self, path, ob):
		#ext=path.split(".")[-1]
		f=open(path, "w")
		f.write(ob.non)
                for x, y in ob.form.items():
                    f.write(Smdt.stag+x+"\n")
                    for blk in y:
                        f.write(Smdt.btag)
                        if blk[0] != "\n":
                            blk = "\n"+blk
                        f.write(blk)
                    
		f.close()
	
	
	
