import sparky
import sputil
class Selection_Error(Exception):
    def __init__(self, message, offset = 0):
        self.parameter = message
        self.offset = offset 
    def __str__(self):
        return repr(self.parameter)
        
class Match:
    def __init__(self, res, peak):
        self.reserved_names = ['and', 'or', 'not', '(', ')']
        self.func_names = ['resid', 'resname', 'name', 'backbone', 'sidechain', 'assigned', 'color', 'height_min', 'height_max', 'volume_min', 'volume_max', 'integrated', 'range_min', 'range_max']
        self.legal_colors = ["black", "white", "gray", "red", "green",
                             "blue", "yellow", "magenta", "cyan",
                             "light_blue", "light_green", "light_yellow",
                             "gold", "orange", "pink", "beige", "turquoise",
                             "coral", "maroon", "purple", "tomato"]
        self.res = res 
        self.peak = peak

    def evaluate(self, expression):
        exp = expression.replace("(", " ( ")
        exp = exp.replace(")", " ) ")
        exp = exp.strip().split()
        if exp == []:
            return True
        evalstr = ""
        i = 0
        while i < len(exp):
            if exp[i] in self.reserved_names:
                evalstr += exp[i] + " "
                i += 1
                continue
            arg, next_i = self.getArg(exp, i)
            #Keword lists
            #resname
            if exp[i] == "resname":
                if len(arg) == 0:
                    raise Selection_Error("Expecting argument after \"rename\"\n" + error_loc(exp, i+1))
                evalstr += str(self.resname(arg)) + " "
            #resid
            elif exp[i] == "resid":
                if len(arg) == 0:
                    raise Selection_Error("Expecting argument after \"resid\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.resid(arg)) + " "
                except:
                    raise Selection_Error("Non-integer resid\n" + error_loc(exp, i+1))
            #name
            elif exp[i] == "name":
                if len(arg) == 0:
                    raise Selection_Error("Expecting argument after \"name\"\n" + error_loc(exp, i+1))
                evalstr += str(self.name(arg)) + " "
            #backbone
            elif exp[i] == "backbone":
                if len(arg) != 0:
                    raise Selection_Error("Unexpected argument after \"backbone\"\n" + error_loc(exp, i+1))
                evalstr += str(self.backbone()) + " "
            #sidechain
            elif exp[i] == "sidechain":
                if len(arg) != 0:
                    raise Selection_Error("Unexpected argument after \"sidechain\"\n" + error_loc(exp, i+1))
                evalstr += str(not self.backbone()) + " "
            #assigned
            elif exp[i] == "assigned":
                try:
                    evalstr += str(self.assigned(arg)) + " "
                except Selection_Error as e:
                    raise Selection_Error("Illegal argument for \"assigned\"\n" + error_loc(exp, i+1+e.offset))
            #color
            elif exp[i] == "color":
                if len(arg) == 0:
                    raise Selection_Error("Expecting argument after \"color\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.color(arg)) + " "
                except Selection_Error as e:
                    raise Selection_Error("Unrecognized color\n" + error_loc(exp, i+1+e.offset))
            #height_min
            elif exp[i] == "height_min":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"height_min\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.height_min(arg)) + " "
                except ValueError:
                    raise Selection("Expecting a numerical argument after \"height_min\"\n" + error_loc(exp, i+1))
            #height_max
            elif exp[i] == "height_max":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"height_max\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.height_max(arg)) + " "
                except ValueError:
                    raise Selection("Expecting a numerical argument after \"height_max\"\n" + error_loc(exp, i+1))
            #volume_min
            elif exp[i] == "volume_min":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"volume_min\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.volume_min(arg)) + " "
                except ValueError:
                    raise Selection("Expecting a numerical argument after \"volume_min\"\n" + error_loc(exp, i+1))
            #volume_max
            elif exp[i] == "volume_max":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"volume_max\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.volume_max(arg)) + " "
                except ValueError:
                    raise Selection("Expecting a numerical argument after \"volume_max\"\n" + error_loc(exp, i+1))
            #integrated:
            elif exp[i] == "integrated":
                if len(arg) != 0:
                    raise Selection_Error("Unexpected argument after \"integrated\"\n" + error_loc(exp, i+1))
                evalstr += str(self.integrated()) + " "
            #range_min
            elif exp[i] == "range_min":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"range_min\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.range_min(arg)) + " "
                except ValueError:
                    raise Selection_Error("Expecting a numerical argument after \"range_min\"\n" + error_loc(exp, i+1))
            #range_max
            elif exp[i] == "range_max":
                if len(arg) != 1:
                    raise Selection_Error("Expecting exactly one argument after \"range_max\"\n" + error_loc(exp, i+1))
                try:
                    evalstr += str(self.range_max(arg)) + " "
                except ValueError:
                    raise Selection_Error("Expecting a numerical argument after \"range_max\"\n" + error_loc(exp, i+1))
            #exception
            else:
                raise Selection_Error("Unrecognized keyword \"%s\"\n"%exp[i] + error_loc(exp, i))

            i = next_i
        return bool(eval(evalstr))

    def getArg(self,exp, i):
        j = i + 1
        while j < len(exp) and (not exp[j] in self.reserved_names):
            if exp[j] in self.func_names:
                raise Selection_Error("Expecting boolean operator before \"%s\"\n" %exp[j] + error_loc(exp, j))
            j += 1
        arg = exp[i+1:j]
        if "to" in arg:
            if len(arg) != 3:
                raise Selection_Error("Unexpected keyword \"to\"\n" + error_loc(exp, i+2))
            return ((arg[0], arg[-1]), j)
        else:
            return (arg,j)

    def resname(self, arg):
        if self.res == None:
            return False
        ret = False
        for each_name in arg:
            ret = ret or self.resname_match(self.res.group.symbol, each_name)
        return ret

    def resid(self,arg):
        if self.res == None:
            return False
        group_id = self.res.group.number
        if isinstance(arg, list):
            l = [int(x) for x in arg]
            return group_id in l
        if isinstance(arg, tuple):
            l = [int(x) for x in list(arg)]
            return group_id != None and group_id >= l[0] and group_id <= l[1]
        
    def color(self, arg):
        colors = [word.lower() for word in arg]
        for j,c in enumerate(colors):
            if c not in self.legal_colors:
                raise Selection_Error("illegal color", j)
        peak_color = self.peak.color.lower().replace(" ","_")
        if peak_color in colors:
            return True
        return False
    
    def name(self, arg):
        if self.res == None:
            return False
        ret = False
        for each_name in arg:
            ret = ret or self.atomname_match(self.res.atom.name, each_name)
        return ret

    def backbone(self):
        return self.name(["C", "N", "CA", "O"]) 

    def assigned(self, arg):
        legal_args = ["ATOM", "RESID", "RESIDUE"]
        for j,a in enumerate(arg):
            if not a in legal_args:
                raise Selection_Error("ILLEGAL ARG", j)
        ret = True
        if "ATOM" in arg or arg ==[]:
            ret = ret and self.res != None and self.res.atom.name != "?"
        if "RESID" in arg or arg ==[]:
            ret = ret and self.res != None and self.res.group.number != None
        if "RESIDUE" in arg or arg ==[]:
            ret = ret and self.res != None and self.res.group.symbol != "?"
        return ret

    def atomname_match(self, name1, name2):
        n1 = name1.strip()
        n2 = name2.strip()
        if n1 == n2:
            return True
        if n2 == "CX" and n1.startswith("C"):
            return True
        return False

    def resname_match(self, res1, res2):
        r1 = res1.strip().lower()
        r2 = res2.strip().lower()
        return convert_residue_symbol(r1) == convert_residue_symbol(r2)

    def height_min(self, arg):
        height = float(arg[0])
        return sputil.peak_height(self.peak) >= height

    def height_max(self, arg):
        height = float(arg[0])
        return sputil.peak_height(self.peak) <= height

    def volume_min(self, arg):
        volume = float(arg[0])
        if self.peak.volume != None:
            return self.peak.volume >= volume
        else:
            return True

    def volume_max(self, arg):
        volume = float(arg[0])
        if self.peak.volume != None:
            return self.peak.volume <= volume
        else:
            return True

    def range_min(self, arg):
        min_range = int(arg[0])
        res = self.peak.resonances()
        if res == None or res[-1] == None or res[-2] == None:
            return False
        r1 = res[-1].group.number
        r2 = res[-2].group.number
        if r1 == None or r2 == None:
            return False
        return min_range <= abs(r1-r2)

    def range_max(self, arg):
        max_range = int(arg[0])
        res = self.peak.resonances()
        if res == None or res[-1] == None or res[-2] == None:
            return False
        r1 = res[-1].group.number
        r2 = res[-2].group.number
        if r1 == None or r2 == None:
            return False
        return max_range >= abs(r1-r2)

    def integrated(self):
        return self.peak.volume != None

def error_loc(exp, i):
    if i >= len(exp):
        return " ".join(exp) + "^"
    exp[i] = "^" + exp[i]
    return " ".join(exp)

def convert_residue_symbol(residue):
    residue_dict = {
        "ala" : "a",
        "ile" : "i",
        "leu" : "l",
        "val" : "v",
        "phe" : "f",
        "trp" : "w",
        "tyr" : "y",
        "asn" : "n",
        "cys" : "c",
        "gln" : "q",
        "met" : "m",
        "ser" : "s",
        "thr" : "t",
        "asp" : "d",
        "glu" : "e",
        "arg" : "r",
        "his" : "h",
        "lys" : "k",
        "gly" : "g",
        "pro" : "p",
    }
    try:
        return residue_dict[residue.lower()]
    except KeyError:
        return residue
