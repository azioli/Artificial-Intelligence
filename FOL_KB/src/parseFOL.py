import ply.lex as lex
import ply.yacc as yacc
def parse_fol(text):
    tokens = ["PREDICATE","LPAREN","RPAREN","NOT","AND","OR","IMPLIES"]
    
    def t_PREDICATE(t):
        r"[A-Z][a-zA-Z]*\((([a-z],)|([A-Z][a-zA-Z]*,))*([a-z]|[A-Z][a-zA-Z]*)\)"
        return t
        
    t_NOT = r"~"
    t_AND = r"&"
    t_OR = r"\|"
    t_IMPLIES = r"=>"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    
    t_ignore = " \t\n"
    
    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)
    
    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        raise ValueError("Syntax error, line {0}: {1}"
                         .format(t.lineno + 1, line)) 
    
    def p_formula_binary(p):
        """FORMULA : LPAREN FORMULA IMPLIES FORMULA RPAREN
                   | LPAREN FORMULA OR FORMULA RPAREN
                   | LPAREN FORMULA AND FORMULA RPAREN"""
        p[0] = [p[3], p[2],p[4]]
    
    def p_formula_not(p):
        "FORMULA : LPAREN NOT FORMULA RPAREN"
        p[0] = [p[2], p[3]]  
        
    def p_formula_symbol(p):
        "FORMULA : PREDICATE"
        p[0] = [p[1]]
                    
    def p_error(p):
        if p is None:
            raise ValueError("Unknown error")
        raise ValueError("Syntax error, line {0}: {1}".format(
                         p.lineno + 1, p.type))
    
    precedence = (("right", "IMPLIES"),
                  ("left", "OR"),
                  ("left", "AND"),
                  ("right", "NOT"))
    
    lexer = lex.lex()
    parser = yacc.yacc()   
    try:
        return parser.parse(text, lexer=lexer)
    except ValueError as err:
        print(err)
