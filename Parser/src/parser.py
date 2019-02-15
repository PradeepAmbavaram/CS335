from lexer import lexer,tokens
import yacc
import sys,getopt

def p_start(p):
    '''start : block
             | statements'''
    p[0]=p[1]
    print(p[0])

def p_block(p):
    '''block : LEFTBRACE statements RIGHTBRACE
             | LEFTBRACE RIGHTBRACE'''
    p[0]=p.slice

def p_statements(p):
    '''statements : statement statements
                  | statement'''
    if (len(p) == 3):
      p[0] = (p[1],p[2])
    else:
      p[0] = p[1]

def p_statement_semicolon(p):
    '''statement : assignment SEMICOLON 
                 | reassignment SEMICOLON 
                 | BREAK SEMICOLON
                 | CONTINUE SEMICOLON
                 | RETURN expression SEMICOLON
                 | expression SEMICOLON
                 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN SEMICOLON
                 | functioncall SEMICOLON 
                 | if
                 | ifelse
                 | whileloop
                 | forloop
                 | funcdecl'''
    if (len(p) == 8):
      p[0] = ('console.log()',p[4],';')
    elif (len(p) == 4):
      p[0] = ('return',p[2],';')
    elif (len(p) == 3):
      p[0] = (p[1],';')
    else:
      p[0] = p[1]


def p_assignment(p):
    '''assignment : VAR assignlist
                  | LEFTPAREN assignment RIGHTPAREN'''

def p_assignlist(p):
    '''assignlist : ID EQ expression COMMA assignlist
                  | ID COMMA assignlist
                  | arraydecl COMMA assignlist
                  | ID EQ expression
                  | ID 
                  | arraydecl'''


def p_reassignment(p):
    '''reassignment : ID EQ expression
                    | ID PLUSEQ expression
                    | ID MINUSEQ expression
                    | ID INTOEQ expression
                    | ID DIVEQ expression
                    | ID INCR
                    | ID DECR
                    | ID LSHIFTEQ expression
                    | ID RSHIFTEQ expression
                    | ID URSHIFTEQ expression
                    | ID ANDEQ expression
                    | ID OREQ expression
                    | ID XOREQ expression
                    | ID MODEQ expression
                    | arraydecl
                    | LEFTPAREN reassignment RIGHTPAREN'''
    if(len(p) == 4 and p[1] == '('):
      p[0] = ('()',p[2])
    elif(len(p) == 3):
      p[0] = ('++',p[1])
      print(p[1])
    elif(len(p) == 2):
      p[0] = p[1]
    else:
      p[0] = (p[2],p[1],p[3])

def p_arraydecl(p):
    '''arraydecl : ID EQ LEFTBRACKET arrayList RIGHTBRACKET'''

def p_arrayList(p):
    '''arrayList : expression COMMA arrayList
                 | arraydecl COMMA arrayList
                 | arraydecl
                 | expression
                 | '''

# Precedence of Operators
precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'BINOR'),
        ('left', 'BINXOR'),
        ('left', 'BINAND'),
        ('left', 'DOUBLEEQ', 'NOTEQUAL', 'STREQUAL', 'STRNEQUAL'),
        ('left', 'LT', 'GT', 'LTE', 'GTE'),
        ('left', 'LSHIFT', 'RSHIFT', 'URSHIFT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'INTO', 'DIVIDE', 'MOD'),
        ('right', 'EXPONENT'),
        ('right', 'NOT', 'BINNOT'),
        )

def p_expression_gen(p):
    '''expression : EVAL LEFTPAREN statements RIGHTPAREN
                  | EVAL LEFTPAREN block RIGHTPAREN'''

def p_expression_op(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression INTO expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression EXPONENT expression'''

def p_groupExp(p):
    '''expression : LEFTPAREN expression RIGHTPAREN
                  | NOT expression'''

def p_expression_binop(p):
    '''expression : expression BINAND expression
                  | expression BINOR expression
                  | expression BINXOR expression
                  | BINNOT expression'''

def p_expression_relop(p):
    '''expression : expression LT expression
                  | expression GT expression
                  | expression DOUBLEEQ expression
                  | expression NOTEQUAL expression
                  | expression LTE expression
                  | expression GTE expression
                  | expression STREQUAL expression
                  | expression STRNEQUAL expression
                  | expression AND expression
                  | expression OR expression'''

def p_expression_shift(p):
    '''expression : expression LSHIFT expression
                  | expression RSHIFT expression
                  | expression URSHIFT expression'''


def p_expression(p):
    '''expression : basicTypes
                  | functioncall
                  | arrayCall
                  | TYPEOF expression'''

def p_arrayCall(p):
    '''arrayCall : ID LEFTBRACKET expression RIGHTBRACKET'''

def p_basicTypes(p):
    '''basicTypes : NUMBER
                  | STRING
                  | ID
                  | UNDEFINED'''

def p_functioncall(p):
    '''functioncall : ID LEFTPAREN argList RIGHTPAREN'''

def p_argList(p):
    '''argList : expression
               | expression COMMA argList
               | '''

def p_if(p):
    '''if : IF expression cblock '''

def p_ifelse(p):
    '''ifelse : IF expression cblock ELSE cblock
              | IF expression cblock ELSE if
              | IF expression cblock ELSE ifelse'''

def p_cblock(p):
    '''cblock : block 
               | statement'''

def p_whileloop(p):
    '''whileloop : WHILE LEFTPAREN expression RIGHTPAREN cblock'''

def p_forloop(p):
    '''forloop : FOR LEFTPAREN ID SEMICOLON cblock'''

def p_initialization(p):
    '''initialization : assignment SEMICOLON initialization
                      | reassignment SEMICOLON initialization
                      | assignment
                      | reassignment'''

def p_increment(p):
    '''increment : reassignment SEMICOLON increment
                 | reassignment'''


def p_funcdecl(p):
    '''funcdecl : FUNCTION ID LEFTPAREN argList RIGHTPAREN cblock
                | VAR ID EQ FUNCTION LEFTPAREN argList RIGHTPAREN cblock SEMICOLON'''

# Error rule for syntax errors
def p_error_semicolon(p):
    '''statement : assignment 
                 | reassignment 
                 | BREAK
                 | CONTINUE
                 | expression
                 | CONSOLE DOT LOG LEFTPAREN expression RIGHTPAREN
                 | functioncall'''
    print("SEMICOLON is missing")

def p_error(p):
    print("Input Error")
    return

parser = yacc.yacc()
t=parser.parse("(i++);",lexer)

print(t)
