import re

def is_implication(p):
    if p[0]=='=>' and len(p)==3:
        return True
    else:
        return False
    
def is_negation(p):
    if p[0]=='~' and len(p)==2 and len(p[1])!=1:
        return True
    else:
        return False

def need_distribution(p): 
    if p[0]=='|':
        for i in range(1,len(p)):
            if len(p[i])>1:
                if p[i][0]=='&':
                    return True
    return False

def unnest(p):
    ret=[]
    if p=='~':
        return p
    
    ret.append(p[0])
    first_op=p[0]
    
    for i in range(1,len(p)):
        if p[i][0]==first_op:
            for j in range(1,len(p[i])):
                ret.append(p[i][j]) 
        else:
            ret.append(p[i])
    
    return ret

def get_simplified(op,literals,current):
    ret=[]
    ret.append(op)
    if len(literals)==1:
        ret.append(literals[0])
    else:
        ret.append(get_simplified(op,literals[0:len(literals)-1],literals[len(literals)-1]))
    ret.append(current) 
    return ret

def simplify(p):
    if len(p)>3:
        p=get_simplified(p[0], p[1:len(p)-1], p[len(p)-1])
    
    for i in range(1,len(p)):
        if len(p[i])>1:
            p[i]=simplify(p[i])
            
    if len(p)>3:
        p=get_simplified(p[0], p[1:len(p)-1], p[len(p)-1])
    
    return p
                
def is_equal(p1,p2):
    if(len(p1)!=len(p2)):
        return False
    else:
        if len(p1)==len(p2)==1:
            if p1==p2:
                return True
            else:
                return False
        else:
            tmp=list(p2)
            for clause in p1:
                try:
                    tmp.remove(clause)
                except ValueError:
                    return False
            return not tmp 

def is_in(x,y):
    for i in range(1,len(x)):
        if is_equal(x[i], y):
            return True
    return False 

def is_variable(p):
    if len(p)==1 and re.match('[a-z]', p[0]):
        return True
    else:
        return False 
    
def eliminate_implication(p):
    ret=[]
    ret.append('|')
    ret.append(['~',p[1]])
    ret.append(p[2])
    return ret

def reduce_negation(p): 
    ret=[]
    if p[1][0]=='|':
        ret.append('&')
    elif p[1][0]=='&':
        ret.append('|')
    elif p[1][0]=='~':
        return p[1][1]
    
    for i in range(1,len(p[1])):
        if len(p[1][i])!=1:
            ret.append(reduce_negation(['~',p[1][i]]))
        else:
            ret.append(['~',p[1][i]])
    return ret

def distribute_or(p):
    ret=[]
    ret.append('&')
    
    if p[1][0]=='&' and p[2][0]=='&':
        ret.append(parse_distribution(['|',p[1][1],p[2][1]]))
        ret.append(parse_distribution(['|',p[1][1],p[2][2]]))
        ret.append(parse_distribution(['|',p[1][2],p[2][1]]))
        ret.append(parse_distribution(['|',p[1][2],p[2][2]])) 
    else:
        if p[1][0]=='&':
            if len(p[2])>2 and need_distribution(p[2]):
                    p[2]=parse_distribution(p[2])
                    ret.append(parse_distribution(['|',p[1][1],p[2][1]]))
                    ret.append(parse_distribution(['|',p[1][1],p[2][2]]))
                    ret.append(parse_distribution(['|',p[1][2],p[2][1]]))
                    ret.append(parse_distribution(['|',p[1][2],p[2][2]]))     
            else:
                ret.append(parse_distribution(['|',p[1][1],p[2]]))
                ret.append(parse_distribution(['|',p[1][2],p[2]]))
        else:
            if len(p[1])>2 and need_distribution(p[1]):
                    p[1]=parse_distribution(p[1])
                    ret.append(parse_distribution(['|',p[1][1],p[2][1]]))
                    ret.append(parse_distribution(['|',p[1][1],p[2][2]]))
                    ret.append(parse_distribution(['|',p[1][2],p[2][1]]))
                    ret.append(parse_distribution(['|',p[1][2],p[2][2]]))                       
            else:
                ret.append(parse_distribution(['|',p[1],p[2][1]]))
                ret.append(parse_distribution(['|',p[1],p[2][2]])) 
    
    return simplify(ret)

def eliminate_duplicate(p):
    if len(p)>2:
        ret=[]
        ret.append(p[0])
        ret.append(p[1])
        for i in range(2,len(p)):
            if not is_in(ret, p[i]):
                ret.append(p[i])
        
        if len(ret)==2:
            ret=ret[1]
        return ret
    else:
        return p
    
def parse_unnest(p):
    p=unnest(p)
    
    for i in range(1,len(p)):
        if len(p)>1:
            p[i]=parse_unnest(p[i])
            
    p=unnest(p)
    
    return p        

def parse_implication(p):
    if is_implication(p):
        p=eliminate_implication(p)
    
    for i in range(1,len(p)):
        if len(p[i])>1:
            p[i]=parse_implication(p[i])
            
    if is_implication(p):
        p=eliminate_implication(p)
    
    return p

def parse_negation(p):
    if is_negation(p):
        p=reduce_negation(p)
    
    for i in range(1,len(p)):
        if len(p[i])>1:
            p[i]=parse_negation(p[i])
    
    if is_negation(p):
        p=reduce_negation(p)
    
    return p
                                                                                           
def parse_distribution(p):
    if need_distribution(p):
        p=distribute_or(p)
        
    for i in range(1,len(p)):
        if len(p[i])>1:
            p[i]=parse_distribution(p[i])
            
    if need_distribution(p):
        p=distribute_or(p)
        
    return simplify(p)

def parse_duplicate(p):
    p=eliminate_duplicate(p)
    
    for i in range(1,len(p)):
        if len(p[i])>1:
            p[i]=eliminate_duplicate(p[i])
            
    p=eliminate_duplicate(p)
    
    return p

def parse_predicate(p):
    ret=[]
    if len(p)>1:
        return ret
    formula=str(p[0])
    lp=formula.find('(')
    rp=formula.find(')')
    ret.append(['pred'])
    ret.append([formula[0:lp]])
    ret.append(formula[lp+1:rp].split(','))
    return ret

var_count=1
    
def get_variables(p,var):
    global var_count
    if len(p)!=3:
        return False
    arg=p[2]
    for i in range(0,len(arg)):
        if is_variable(arg[i]) and arg[i] not in var:
            var[arg[i]]=str(var_count)
            var_count+=1

def change_variable(s,key,var):
    s=s.replace('('+key+')','('+var[key]+')')
    s=s.replace('('+key+',','('+var[key]+',')
    s=s.replace(','+key+')',','+var[key]+')')
    s=s.replace(','+key+',',','+var[key]+',')
    return s
       
def standardize(p):
    ret=[]
    if len(p)>2 and p[0]=='&':
        ret=p[1:len(p)]
    else:
        ret=[p]
    for s in ret:
        var={}
        if len(s)==1:
            tmp=parse_predicate([s[0]])
            get_variables(tmp, var)
            for key in var.keys():
                s[0]=change_variable(s[0], key, var)
        elif len(s)==2 and s[0]=='~':
            tmp=parse_predicate(s[1])
            get_variables(tmp, var) 
            for key in var.keys():
                s[1][0]=change_variable(s[1][0], key, var)   
        elif s[0]=='|':
            for i in range(1,len(s)):
                if len(s[i])==1:
                    tmp=parse_predicate([s[i][0]])
                elif len(s[i])==2 and s[i][0]=='~':
                    tmp=parse_predicate(s[i][1])
                get_variables(tmp, var)
            for i in range(1,len(s)):
                if len(s[i])==1:
                    for key in var.keys():
                        s[i][0]=change_variable(s[i][0], key, var)
                elif len(s[i])==2 and s[i][0]=='~':
                    for key in var.keys():
                        s[i][1][0]=change_variable(s[i][1][0], key, var)                                                 
    return ret 
        
def fol_to_cnf(p):
    if len(p)==0:
        return p
    
    ret=parse_implication(p)
    ret=parse_negation(ret)
    ret=simplify(ret)
    ret=parse_distribution(ret)
    ret=parse_unnest(ret)
    ret=parse_duplicate(ret)
    ret=standardize(ret)
    return ret
