import parseFOL,FOLtoCNF
import re,copy
from sre_compile import isstring

class KnowledgeBase:
    def __init__(self):
        self.truth=[]
        self.ref=[]
    
    def append(self,plist):
        if is_truth_clause(plist):
            self.truth.append(plist)   
        else:
            self.ref.append(plist)
    
    def get_length(self):
        return len(self.truth)+len(self.ref)        

class PredicateTable:
    def __init__(self):
        self.truth={}
        self.ref={}
                    
class Sentence:
    def __init__(self):
        self.predicates=[]
        
class Predicate:
    def __init__(self,symbol,neg,args):
        self.symbol=symbol
        self.negation=neg
        self.args=args 
    def __lt__(self,other):
            return self.symbol[0] < other.symbol[0]
        
class Predicate_info:
    def __init__(self,symbol):
        self.symbol=symbol
        self.len=0
        self.arglist=[]
        self.neglist=[]
        self.numlist=[] 
                   
def is_variable(p):
    if isinstance(p,list) and len(p)==1 and isstring(p[0]) and re.match('[0-9]+', p[0]):
        return True
    elif isstring(p) and re.match('[0-9]+', p):
        return True 
    else:
        return False
   
def is_predicate(p):
    return isinstance(p, Predicate)  

def is_truth_clause(p):
    if is_predicate(p):
        for arg in p.args:
            if not is_variable(arg):
                return True
        return False
    elif isinstance(p, list):
        if len(p)>1:
            return False
        elif is_truth_clause(p[0]):
            return True
        else:
            return False

def parse_query(formula):
    if formula[0]=='~':
        neg=False
        ret=parse_predicate([formula[1:len(formula)]], neg)
    else:
        neg=True
        ret=parse_predicate([formula[0:len(formula)]], neg)
    return ret  
          
def parse_predicate(p,neg):
    formula=str(p[0])
    lp=formula.find('(')
    rp=formula.find(')')
    ret=Predicate([formula[0:lp]],neg,formula[lp+1:rp].split(','))
    return ret

def unify(x,y,subs):
    if subs==False:
        return False
    elif x==y:
        return subs
    elif is_variable(x):
        return unify_var(x,y,subs)
    elif is_variable(y):
        return unify_var(y,x,subs)
    elif is_predicate(x) and is_predicate(y):
        return unify(x.args,y.args,unify(x.symbol,y.symbol,subs))
    elif len(x)==len(y) and len(x)>1 and len(y)>1:
        if len(x)==2:
            return unify([x[1]],[y[1]],unify([x[0]],[y[0]],subs))
        else:
            return unify(x[1:len(x)],y[1:len(y)],unify([x[0]],[y[0]],subs))
    else:
        return False

def unify_var(var,x,subs):
    if var[0] in subs.keys():
        return unify([subs[var[0]]],x,subs)
    elif x[0] in subs.keys():
        return unify(var,[subs[x[0]]],subs)
    elif var[0]==x[0]:
        return False
    else:
        subs[var[0]]=x[0]
        return subs

def do_substitution(x,subs):
    if not x or not subs:
        return
    for p in x:
        for i in range(len(p.args)):
            arg=(p.args)[i]
            if arg in subs.keys():
                (p.args)[i]=subs[arg]

def resolution(x,y):
    ret=[]
    resolved=False
    for i in range(len(x)):
        for j in range(len(y)):
            if x[i].symbol==y[j].symbol and x[i].negation==(not y[j].negation):
                subs={}
                if not (unify(x[i],y[j],subs)is False):
                    tmpx=copy.deepcopy(x)
                    tmpy=copy.deepcopy(y)
                    tmpx.pop(i)
                    tmpy.pop(j)
                    if not tmpx and not tmpy:
                        return []
                    do_substitution(tmpx, subs)
                    do_substitution(tmpy, subs)
                    tmp_ret=tmpx+tmpy   
                    merge_plist(tmp_ret)
                    if tmp_ret:
                        ret.append(tmp_ret)
                        resolved=True                
    if resolved:
        return ret
    else:
        return False
    
def merge_plist(plist):
    plist_len=len(plist)
    if plist_len<2:
        return
    for i in range(plist_len):
        for j in range(i+1,plist_len):
            if plist[i].symbol==plist[j].symbol and arglist_equal(plist[i].args, plist[j].args,True):
                if plist[i].negation==(not plist[j].negation):
                    pi=plist[i]
                    pj=plist[j]
                    plist.remove(pi)
                    plist.remove(pj)
                    merge_plist(plist)
                    return
                else:
                    pj=plist[j]
                    plist.remove(pj)
                    merge_plist(plist)
                    return
    return        


def standardize_variables(plist):
    vardir={}
    for p in plist:
        for arg in p.args:
            if is_variable([arg]) and arg not in vardir.keys():
                vardir[arg]=str(FOLtoCNF.var_count)
                FOLtoCNF.var_count+=1
    for p in plist:
        for i in range(len(p.args)):
            arg=(p.args)[i]
            if is_variable([arg]) and arg in vardir.keys():
                (p.args)[i]=vardir[arg]
                        
def update_ptable(plist,KB,ptable):
    if is_truth_clause(plist):
        base=KB.truth
        table=ptable.truth
    else:
        base=KB.ref
        table=ptable.ref
    for p in plist:
        num=len(base)
        if p.symbol[0] not in table:
            info=Predicate_info(p.symbol[0])
            info.arglist.append(p.args)
            info.neglist.append(p.negation)
            info.numlist.append(num)
            info.len+=1
            table[p.symbol[0]]=info
        else:
            info=table[p.symbol[0]]
            info.arglist.append(p.args)
            info.neglist.append(p.negation)
            info.numlist.append(num)
            info.len+=1

def predicates_equal(p1,p2):
    subs={}
    return do_predicates_equal(p1, p2, subs)

def item_equal(p1,p2):
    if p1.symbol[0]!=p2.symbol[0] or p1.negation!=p2.negation or len(p1.args)!=len(p2.args):
        return False
    for i in range(len(p1.args)):
        if is_variable([p1.args[i]]) and not is_variable([p2.args[i]]):
            return False
        elif not is_variable([p1.args[i]]) and is_variable([p2.args[i]]):
            return False
        elif not is_variable([p1.args[i]]) and not is_variable([p2.args[i]]):
            if p1.args[i]!=p2.args[i]:
                return False
    subs={}
    if unify(p1.args, p2.args, subs) is False:
        return False 
    value_set=set()
    if subs:
        for value in subs.values():
            if value not in value_set:
                value_set.add(value)
            else:
                return False   
    return True

def do_predicates_equal(p1,p2,subs):
    if not p1 and not p2:
        return True
    if len(p1)==len(p2)==1 and item_equal(p1[0],p2[0]):
        return True
    for j in range(len(p2)):
        if item_equal(p1[0],p2[j]):
            tmpsubs=copy.deepcopy(subs)
            if not unify(p1[0],p2[j],tmpsubs) is False:
                tmp1=copy.deepcopy(p1)
                tmp2=copy.deepcopy(p2)
                tmp1.pop(0)
                tmp2.pop(j)
                do_substitution(tmp1, tmpsubs)
                do_substitution(tmp2, tmpsubs)
                if do_predicates_equal(tmp1,tmp2,tmpsubs):
                    return True    
    return False
            
def arglist_equal(arglist1,arglist2,subbed):
    if len(arglist1)!=len(arglist2):
        return False
    for i in range(len(arglist1)):
        if subbed and arglist1[i]!=arglist2[i]:
            return False
        else:
            if is_variable([arglist1[i]]) and not is_variable([arglist2[i]]):
                return False
            elif not is_variable([arglist1[i]]) and is_variable([arglist2[i]]):
                return False
            elif not is_variable([arglist1[i]]) and not is_variable([arglist2[i]]) and arglist1[i]!=arglist2[i]:
                return False
            else:
                subs={}
                if unify(arglist1, arglist2, subs) is False:
                    return False
                if subs:
                    value_set=set()
                    for value in subs.values():
                        if value not in value_set:
                            value_set.add(value)
                        else:
                            return False   
    return True
                 
def occur_check(plist,KB,ptable):
    if is_truth_clause(plist):
        base=KB.truth
        table=ptable.truth
        p=plist[0]
        symbol=p.symbol[0]
        if symbol not in table.keys():
            return False
        else:
            info=table[symbol]
            for i in range(info.len):
                if arglist_equal(info.arglist[i], p.args, False) and info.neglist[i]==p.negation:
                    return True
            return False    
    else:
        base=KB.ref
        table=ptable.ref
        
    occur_set=set()
    for p in plist:
        symbol=p.symbol[0]
        if symbol not in table.keys():
            return False
        else:
            info=table[symbol]
            occur_list=[]
            for i in range(info.len):
                if arglist_equal(info.arglist[i], p.args,False) and info.neglist[i]==p.negation:
                    if len(plist)==len(base[info.numlist[i]]):
                        occur_list.append(info.numlist[i])
            if not occur_set:
                occur_set=set(occur_list)
            else:
                occur_set=occur_set.intersection(occur_list) 
        if not occur_set:
            return False
    for i in occur_set:
        if predicates_equal(plist, base[i]):
            return True    
    return False     

def resolution_inference(q,original_KB,original_ptable):
    tmp_var_count=FOLtoCNF.var_count
    
    if occur_check([q], original_KB, original_ptable) :
        return True
    
    notq=Predicate(q.symbol,not q.negation,q.args) 
    if occur_check([notq], original_KB, original_ptable):
        return False
    
    KB=copy.deepcopy(original_KB)
    ptable=copy.deepcopy(original_ptable)
    update_ptable([notq], KB, ptable)
    KB.append([notq])  
    
    new_clauses=[]
    pairs=set() 
    while True:
        pairs.clear()
        for symbol in ptable.truth.keys():
            if symbol not in ptable.ref.keys():
                continue
            info1=ptable.truth[symbol]
            info2=ptable.ref[symbol]
            len1=info1.len
            len2=info2.len
            for i in range(len1):
                for j in range(len2):
                    if info1.neglist[i]==(not info2.neglist[j]):
                        pairs.add((info1.numlist[i],info2.numlist[j]))
        
        for num1,num2 in pairs:
            ret=resolution(KB.truth[num1], KB.ref[num2])
            if ret is False:
                continue  
            elif not ret:
                FOLtoCNF.var_count=tmp_var_count
                return True
            else:
                for plist in ret:
                            
                    if is_truth_clause(plist):
                        p=plist[0]                            
                        not_plist=[Predicate(p.symbol,not p.negation,p.args)]                            
                        if occur_check(not_plist, KB, ptable):
                            FOLtoCNF.var_count=tmp_var_count
                            return True
                    new_clauses.append(plist) 
                                                        
        len_KB=KB.get_length()
        for plist in new_clauses:
                
            if not occur_check(plist, KB, ptable):
                update_ptable(plist, KB, ptable)
                KB.append(plist)
        if len_KB==KB.get_length():
            FOLtoCNF.var_count=tmp_var_count
            return False
                                                                                
if __name__ == "__main__":
    fo=open("input.txt","r+")
    query_num=int(fo.readline().strip())
    querys=[]
    for i in range(query_num):
        formula=fo.readline().strip()
        formula=''.join(formula.split())
        q=parse_query(formula)
        querys.append(q)

    given_num=int(fo.readline().strip())
    given=[]
    for i in range(given_num):
        given.append(fo.readline().strip())
    formulas=[]    
    for i in range(given_num):
        formula=given[i]
        formula=''.join(formula.split())
        formula=parseFOL.parse_fol(formula)
        formula=FOLtoCNF.fol_to_cnf(formula)
        if len(formula)==1:
            formulas.append(formula)
        elif len(formula)>1:
            for j in range(len(formula)):
                formulas.append([formula[j]])
    
    KB=KnowledgeBase()
    ptable=PredicateTable()
    
    for i in range(len(formulas)):
        formula=formulas[i]
        plist=[]             
        if len(formula[0])==1:
            p=parse_predicate(formula[0], True)
            plist.append(p)
        elif len(formula[0])==2 and formula[0][0]=='~':
            p=parse_predicate(formula[0][1],False)
            plist.append(p)
        elif len(formula[0])>2 and formula[0][0]=='|':
            for j in range(1,len(formula[0])):
                if len(formula[0][j])==1:
                    p=parse_predicate(formula[0][j], True)
                    plist.append(p)
                elif len(formula[0][j])==2 and formula[0][j][0]=='~':
                    p=parse_predicate(formula[0][j][1],False)
                    plist.append(p)    
        if occur_check(plist, KB,ptable):
            continue
        update_ptable(plist, KB, ptable) 
        KB.append(plist)
        
    fw=open('output.txt',"w") 
    for q in querys:
        ret=resolution_inference(q, KB, ptable)
        if ret:
            print("TRUE",file=fw)
        else:
            print("FALSE",file=fw)        