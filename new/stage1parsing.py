import yacc
from lexer import lexFunc,lexer,tokens
import sys
import os
import pprint
#output = []

temp_count=0
string_count=0
labels = 0
num_scopes = 0
function_count = 0
label_base = 'label'
temp_base = 'Temporarie'
scope_base = 'scope'
function_base = 'function'


st={}
st['0']={}
st['0']['level']=0
st['0']['vars']=[]
st['0']['funs']=[]
st['scopes']=[st['0']]
st['address']={}


var = {}
var['t']= 'int'
var['s']=0
var['p']= 'zerotemp'
var['d']= 2019

offset = 0

def newvarforscope(type,level,place,data):
	var = {}
	var['t']=type
	var['s']=level
	var['p']=place
	var['d']=data
	return var

def createtemp(var,scope,type,data):
	global temp_count,temp_base
	new = temp_base + str(temp_count)
	temp_count += 1

	scope[var]=newvarforscope(type,scope['level'],new,data)
	scope['vars'].append(var)
	#Address Descriptor
	st['address'][new]={'scope':scope,'variable':var}
	return new

def newtemp():
	global temp_count,temp_base
	new = temp_base + str(temp_count)
	temp_count += 1	
	#Address_Descriptor
	st['address'][new]={'scope':st['scopes'][len(st['scopes'])-1],'variable':''}
	return new

def newdict(l):
	new ={}
	size=len(l)
	i=0
	while i <= size/2:
		new[l[i]]=l[i+1]
		i=i+2
	return new

def id_present(id,type):
	scopes =st['scopes']
	flag = False
	count = 0
	for s in reversed(scopes):
		count  +=1
		if type == 'variable':
			l = s['vars']
		else:
			l = s['funs']

		if id in l:
			flag = True
			return (flag,len(scopes)-count)
	return (flag,-1)

def createlabel():
	global labels, label_base
	label = label_base + str(labels)
	labels += 1
	if labels > 120:
		print "ERROR:Infinite loop"	
		sys.exit()
	return label



def addscope():
	global num_scopes
	num_scopes +=1
	new = str(num_scopes)
	st[new]={}
	st[new]['level']=len(st['scopes'])
	st[new]['vars']=[]
	st[new]['funs']=[]
	st['scopes'].append(st[new])

def removescope():
	st['scopes'].pop()

def createfun(iden):
	global function_base, function_count
	new= function_base+str(function_count)
	function_count += 1

	this= st['scopes'][len(st['scopes'])-1]
	this[iden] = newvarforscope('FUNCTION',this['level'],new,data={})
	this['funs'].append(iden)
	return new

def loop_and_print(o,name):
	global offset
	elements = o['elements']
	for temp in range(elements):
		processing_obj=o['array'][temp]
		if processing_obj['elements']>1:
			loop_and_print(processing_obj,name)
		else:
			print "AI=, "+name+", "+str(offset)+", "+processing_obj['place']
			offset = offset +4
	#Remaining	

def getshape(o,arr):
	elements = o['elements']
	arr.append(elements)
	processing_obj = o['array'][0]
	if processing_obj['elements']>1:
		arr = getshape(processing_obj,arr)
	else:
		arr.append(1)
	return arr
	


##SemanticRules##



def p_start(p):
	'''start : block  
			 | statements'''


def p_block(p):
	'''block : LEFTBRACE blockmarker statements RIGHTBRACE'''
	removescope()


def p_blockmarker(p):
	'''blockmarker : '''
	addscope()


def p_statements(p):
	'''statements : statement statements 
				  | statement'''



def p_statement_semicolon(p):
	'''statement : assignment SEMICOLON
				 | declaration SEMICOLON 
				 | reassignment SEMICOLON 
				 | BREAK SEMICOLON
				 | CONTINUE SEMICOLON
				 | funcstmt SEMICOLON
				 | if
				 | ifelse
				 | whileloop
 				 | funcdecl
 				 | forloop
 				 | reassignmentarray SEMICOLON'''

def p_return_expression(p):
	'''statement : RETURN expression SEMICOLON'''
	print "push, "+p[2]['place']
	print "ret"
	
def p_statement_print(p):
	'''statement : CONSOLE DOT LOG LEFTPAREN printList RIGHTPAREN SEMICOLON'''
	for var in p[5]:
		print "print, "+var['place']
 
def p_printList(p):
	'''printList : expression COMMA printList'''
	var = newdict(['type',p[1]['type'],'place',p[1]['place']])
	p[0] = [var] + p[2]
 
def p_printList_base(p):
	'''printList : expression'''
	var = newdict(['type',p[1]['type'],'place',p[1]['place']])
	p[0] = [var]

#Declaration
def p_declaration(p):
	'''declaration : VAR declarationList'''
	this = st['scopes'][len(st['scopes'])-1]
	for var in p[2]:
		if var not in this['vars']:
			createtemp(var,this,type="UNDEFINED",data={})
		else:
			raise SyntaxError

def p_declarationList(p):
	'''declarationList : ID COMMA declarationList'''
	p[0] = [p[1]] + p[3]

def p_declaration_base(p):
	'''declarationList : ID'''
	p[0] = [p[1]]
	
#Assignment
def p_assignment(p):
	'''assignment : VAR assignlist'''
	this = st['scopes'][len(st['scopes'])-1]
	for var in p[2]:
		if var in this['vars']:
			print "Redefined Variable"
			raise SyntaxError
		else:
			if var['type']!='ARRAY':
				new = createtemp(var['name'],this,var['type'],data={})
				print "=, "+new+", "+var['place']
			else:
				new = createtemp(var['name'],this,var['type'],var['data'])

def p_assignlist(p):
	'''assignlist : ID EQ expression COMMA assignlist'''
	id = {}
	id['name'] = p[1]
	id['type'] = p[3]['type']
	id['place'] = p[3]['place']
	p[0] = [id] + p[5]

def p_assignlist_base(p):
	'''assignlist : ID EQ expression'''
	id = {}
	id['name'] = p[1]
	id['type'] = p[3]['type']
	id['place'] = p[3]['place']
	p[0] = [id]

def p_assignlist_array(p):
	'''assignlist : ID EQ array'''
	id = {}
	id['name'] = p[1]
	id['type'] = 'ARRAY'
	id['place'] = newtemp()
	id['data'] = p[3]	

	offset = 0
	shape = []
	arr= []
	arr = getshape(p[3],shape)
	id['data']['shape']=arr
	size = 4

	for el in arr:
		size = size *el

	print "array_def, "+p[1]+", "+str(size)
	loop_and_print(p[3], p[1])
	p[0] = [id]

#Reassignment
def p_assignment_arith(p):
	'''reassignment : ID EQ expression
				| ID PLUSEQ expression
				| ID MINUSEQ expression
				| ID INTOEQ expression
				| ID DIVEQ expression'''
	p[0]={}
	this = st['scopes'][len(st['scopes'])-1]
	flag,scope = id_present(p[1],'variable')
	if flag:
		dst = st['scopes'][scope][p[1]]
		src = p[3]
		if p[2]!= "=":
			if dst['t']!=src['type'] or dst['t']=="STRING":
				print "Reassignment types not matching"
				raise SyntaxError

		dst = dst['p']
		src = src['place']

		if p[2]=="=":
			print "=, "+dst+", "+src
		elif p[2]=='+=':
			print "+, "+dst+", "+src
		elif p[2]=='-=':
			print "-, "+dst+", "+src
		elif p[2]=='*=':
			print "*, "+dst+", "+src
		elif p[2]=='/=':
			print "/, "+dst+", "+src
		elif p[2]=='%=':
			print "%, "+dst+", "+src

		if scope != len(st['scopes'])-1:
			this['vars'].append(p[1])
			this[p[1]]=newvarforscope(p[3]['type'],len(st['scopes'])-1,dst,data={})


	else:
		print p[1] + "identifier not defined"
		raise SyntaxError

def p_reassignment_incr(p):
	'''reassignment : ID INCR
					| ID DECR'''
	p[0]={}
	this = st['scopes'][len(st['scopes'])-1]
	flag,scope = id_present(p[1],'variable')
	if flag:
		dst = st['scopes'][scope][p[1]]
		temp = newtemp()
		print "B=, "+temp+", 1"

		if p[2]=="++":
			print "+, "+dst['p']+", "+temp
		elif p[2]=='--':
			print "-, "+dst['p']+", "+temp	
		if scope != len(st['scopes'])-1:
			this['vars'].append(p[1])
			this[p[1]] = newvarforscope(dst['t'],len(st['scopes'])-1,dst['p'],data={})

def p_reassignment_shift(p):
	'''reassignment	: ID LSHIFTEQ expression
					| ID RSHIFTEQ expression
					| ID URSHIFTEQ expression
					| ID ANDEQ expression
					| ID OREQ expression
					| ID XOREQ expression
					| ID MODEQ expression
					| LEFTPAREN reassignment RIGHTPAREN'''

def p_array(p):
	'''array : LEFTBRACKET arrayList RIGHTBRACKET'''
	p[0] = newdict(['elements',p[2]['elements'],'array',p[2]['array'],'type','ARRAY']) 

def p_arrayList_array(p):
	'''arrayList : array COMMA arrayList'''
	temp = {}
	temp['type'] = 'ARRAY'
	temp['elements'] = p[1]['elements']
	temp['array'] = p[1]['array']

	p[0] = newdict(['elements',1+ p[3]['elements'],'array',[temp] + p[3]['array']])

def p_arrayList_base_array(p):
	'''arrayList : array'''
	temp = {}
	temp['type'] = 'ARRAY'
	temp['elements'] = p[1]['elements']
	temp['array'] = p[1]['array']	
	p[0] = newdict(['elements',1,'array',[temp]])

def p_arrayList_exp(p):
	'''arrayList : expression COMMA arrayList'''
	if p[1]['type']!='NUMBER':
		print "expression not a NUMBER, Check p_arrayList_base_exp"
		raise SyntaxError

	else:
		temp = {}
		temp['type'] = 'NUMBER'
		temp['elements'] = 1
		temp['place'] = p[1]['place']		
		p[0] = newdict(['elements',1+ p[3]['elements'],'array',[temp]+ p[3]['array']])

def p_arrayList_base_exp(p):
	'''arrayList : expression'''
	if p[1]['type']!='NUMBER':
		print "expression not a NUMBER, Check p_arrayList_base_exp"
		raise SyntaxError
	else:
		temp = {}
		temp['type'] = 'NUMBER'
		temp['elements'] = 1
		temp['place'] = p[1]['place']

		p[0] = {}
		p[0]['array'] = [temp]
		p[0]['elements'] = 1

#precedence
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
		('right', 'NOT', 'BINNOT'),
		)

#ArithmeticOperations
def p_expression_op(p):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression INTO expression
				  | expression DIVIDE expression
				  | expression MOD expression'''
	new = newtemp()
	if p[1]['type']!=p[3]['type']:
		print "Types not matching"	
	else:
		p[0]=newdict(['type',p[1]['type'],'place',new])
		print "=, "+p[0]['place']+", "+p[1]['place']
		print p[2]+", "+p[0]['place']+", "+p[3]['place']		

#Group
def p_groupExp(p):
	'''expression : LEFTPAREN expression RIGHTPAREN'''
	p[0]=newdict(['type',p[2]['type'],'place',p[2]['place']])

#Not_of_Expression
def p_expression_not(p):
	'''expression : NOT expression'''
	if p[2]['type']=='BOOLEAN':
		p[0]=newdict(['place',p[2]['place']])
		t = newtemp()
		print "B=, "+t+", 1"
		print "+, "+p[0]['place']+", "+t
		print "B=, "+t+", 2"
		print "%, "+p[0]['place']+", "+t
	else:
		print "NOT Expression is not boolean" 	
		raise SyntaxError

def p_expression_binop(p):
	'''expression : expression BINAND expression
				  | expression BINOR expression
				  | expression BINXOR expression
				  | BINNOT expression'''

#RelationalOperations
def p_expression_relop(p):	
	'''expression : expression LT expression
				  | expression GT expression
				  | expression DOUBLEEQ expression
				  | expression NOTEQUAL expression
				  | expression LTE expression
				  | expression GTE expression'''

	new = newtemp()
	p[0]=newdict(['type','BOOLEAN','place',new])
	if p[2]=='<':
		op='jl'
	elif p[2]=='>':
		op = 'jg'
	elif p[2]=='==':
		op = 'je'
	elif p[2]=='!=':
		op = 'jne'
	elif p[2]=='<=':
		op = 'jle'
	elif p[2]=='>=':
		op = 'jge'

	l1= createlabel()
	l2= createlabel()
	l3= createlabel()
	print "ifgoto, "+op+", "+p[1]['place']+", "+p[3]['place']+", "+l1
	print "goto, "+l2
	print "label, "+l1
	print "B=, "+p[0]['place']+", 1"
	print "goto, "+l3
	print "label, "+l2
	print "B=, "+p[0]['place']+", 0"
	print "label, "+l3

def p_expression_strop(p):
	'''expression : expression STREQUAL expression
				  | expression STRNEQUAL expression'''

#ANDOR
#EVAL
# def p_expression_eval_undefined(p):
# 	'''expression : EVAL LEFTPAREN evalmarker statements evalendmarker RIGHTPAREN
# 				  | EVAL LEFTPAREN block RIGHTPAREN'''
# 	new =newtemp()
# 	p[0]=newdict(['type','EVAL_UNDEFINED','place',new,'value',0])


# def p_expression_eval_expression(p):
# 	'''expression : EVAL LEFTPAREN expression RIGHTPAREN'''
# 	new =newtemp()
# 	p[0]=newdict(['type',p[3]['type'],'place',new])
# 	if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
# 		print "=, "+p[0]['place']+', '+p[3]['place']
# 	else:
# 		print "check expression eval expression"

# def p_evalmarker(p):
# 	'''evalmarker : '''
# 	addScope()

# def p_evalendmarker(p):
# 	'''evalendmarker : '''
# 	removeScope()


#ExpressionBasics
def p_expression_basic(p):
	'''expression : basicTypes'''
	new = newtemp()
	p[0]=newdict(['type',p[1]['type'],'place',new])
	if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
		print "B=, "+p[0]['place']+', '+str(p[1]['value'])
	else:
		"check definition"

#ExpressionID
def p_expression_id(p):
	'''expression : ID'''
	flag,scope  = id_present(p[1],'variable')
	if flag:
		src = st['scopes'][scope][p[1]]
		p[0]=newdict(['type',src['t'],'place',src['p']])
		if p[0]['type'] in ['BOOLEAN', 'NUMBER', 'UNDEFINED']:
			t=1
		else:
			"check definiton"

	else:
		print p[1]+" is NOT DEFINED"
		raise SyntaxError

def p_expression_type(p):
	'''expression : TYPEOF expression'''
	new = newtemp()
	p[0]=newdict(['value',p[2]['type'],'place',new,'type','STRING'])

def p_expression_functioncall_id(p):
	'''funcstmt : ID EQ functioncall'''
	flag,scope=id_present(p[1],'variable')
	if flag:
		dst = st['scopes'][scope][p[1]]
		src = p[3]
		if p[2]!="=":
			if dest['type']!=src['type']:
				print "Reassignment types not matching"
				raise SyntaxError
			dst = dst['place']
			src = src['place']
			scope=p[3]['level']
			place=p[3]['place']
			temp=st['scopes'][scope][p[1]]['place']
			print "call, "+st['scopes'][scope][place]['place']+", "+temp
	else:
		print p[1]+" is not defined Already"

def p_expression_functioncall(p):
	'''funcstmt : functioncall'''
	scope=p[1]['level']
	place = p[1]['place']
	print "call, "+st['scopes'][scope][place]['place']

def p_expression_functioncall_varid(p):
	'''funcstmt : VAR ID EQ functioncall'''
	this = st['scopes'][len(st['scopes'])-1]
	variable=p[2]
	if variable not in this['vars']:
		createtemp(variable,this,"UNDEFINED",data={})
		print p[4]
		scope = p[4]['level']
		place=p[4]['place']
		print "call, "+st['scopes'][scope][place]['p']+", "+this[variable]['p']
	else:
		raise SyntaxError
	new=newtemp()
	p[0]=newdict(['type','FUNCTIONCALL','place',new])
	print "pop, " + p[0]['place']

def p_expression_arraycall(p):
	'''expression : arrayCall'''
	val_in_addr = p[1]['val_in_addr']
	addr = p[1]['addr']

	p[0]=newdict(['type','NUMBER','place',val_in_addr])
	print "val, "+val_in_addr+", "+addr

def p_reassignment_array(p):
	'''reassignmentarray : arrayCall EQ expression'''
	addr = p[1]['addr']
	val_in_addr = p[1]['val_in_addr']
	print "updatearr, "+addr+", "+p[3]['place']

def p_arrayCall(p):
	'''arrayCall : ID reference'''
	flag,scope = id_present(p[1],'variable')
	if not flag:
		print "variable being referenced does not exist"
		raise SyntaxError

	else:
		array_ptr = st['scopes'][scope][p[1]]
		shape = array_ptr['d']['shape']
		if len(p[2])!=len(shape)-1:
			print "shape of the array and your referencing doesnot match"
			raise SyntaxError
		else:
			add= newtemp()
			print "addr, "+add+", "+p[1]
			tt=newtemp()
			for i in range(len(p[2])):
				t = i +1 
				multipland = 1
				while t < len(shape):
					multipland=multipland*shape[t]
					t=t+1
				print "B=, "+tt+", "+str(multipland*4)
				print "*, "+p[2][i]['place']+", "+tt

			for i in range(len(p[2])):
				print "+, "+add+", "+p[2][i]['place']

			val_in_addr=newtemp()
			p[0]=newdict(['val_in_addr',val_in_addr,'addr',add,'type','NUMBER','place',val_in_addr])  
		
def p_reference(p):
	'''reference : LEFTBRACKET expression RIGHTBRACKET reference'''
	if p[2]['type']!='NUMBER':
		print "Array index has to be number"
		raise SyntaxError
	else:
		temp=newdict(['type',p[2]['type'],'place',p[2]['place']])
		p[0]=[temp]+p[4]

def p_reference_base(p):
	'''reference : LEFTBRACKET expression RIGHTBRACKET'''
	if p[2]['type']!='NUMBER':
		print "Array index has to be number"
		raise SyntaxError
	else:
		temp=newdict(['type',p[2]['type'],'place',p[2]['place']])
		p[0]=[temp]

#BASICTYPES
def p_basicTypes_number(p):
	'''basicTypes : NUMBER'''
	p[0]=newdict(['type','NUMBER','value',p[1]])

def p_basicTypes_boolean(p):
	'''basicTypes : BOOLEAN'''
	if p[1] == 'true':
		value = 1
	else:
		value = 0
	p[0]=newdict(['type','BOOLEAN','value',value])

def p_basicTypes_string(p):
	'''basicTypes : STRING'''
	global string_count
	p[0]=newdict(['type','STRING','value',p[1],'ref','__string'+str(string_count)+'__'])
	string_count+=1

def p_basicTypes_undefined(p):
	'''basicTypes : UNDEFINED'''
	p[0]['type']='UNDEFINED'
	p[0]['value']=0


#FunctionCall
def p_functioncall(p):
	'''functioncall : ID LEFTPAREN argList RIGHTPAREN'''
	flag,scope = id_present(p[1],'funtion')
	if flag:
		for par in reversed(p[3]):
			print "param, "+par
		p[0]=newdict(['level',scope,'place',p[1]])
	else:
		print "No function named ",p[1]," Already defined"

def p_arglist_expr(p):
	'''argList : expression'''
	p[0] = [p[1]['place']]	

def p_argList(p):
	'''argList : expression COMMA argList'''
	p[0] = [p[1]['place']] + p[3]

def p_argList_base(p):
	'''argList : '''
	p[0] = []

#IFBLOCK
def p_if(p):
	'''if : IF expression ifelseblock block ifblockend'''

def p_ifblockendmarker(p):
	'''ifblockend : '''
	print "label, "+p[-2][1]

#IFELSE
def p_ifelse(p):
	'''ifelse : IF expression ifelseblock block ELSE elseblock block elseblockend'''

def p_ifelseblock_marker(p):
	'''ifelseblock : '''
	l1=createlabel()
	l2=createlabel()
	l3=createlabel()
	p[0]=[l1,l2,l3]

	t=newtemp()

	print "B=, "+t+", 1"
	print "ifgoto, je, "+p[-1]['place']+", "+t+", "+l1
	print "goto, "+l2
	print "label, "+l1

def p_elseblock_marker(p):
	'''elseblock : empty'''
	print "goto, "+p[-3][2]
	print "label, "+p[-3][1]

def p_elseblockend_marker(p):
	'''elseblockend : empty'''
	print "label, "+p[-5][2]	

#While
def p_whileloop(p):
	'''whileloop : WHILE whileblockstart LEFTPAREN expression RIGHTPAREN exprcheck block whileblockend'''

def p_whileblockstart(p):
	'''whileblockstart : empty'''
	start = createlabel()
	end = createlabel()
	p[0]=[start,end]
	print "label, "+start

def p_exprcheck(p):
	'''exprcheck : empty'''
	t = newtemp()
	print "B=, "+t+", 1"
	print "ifgoto, jne, "+p[-2]['place']+", "+t+", "+p[-4][1]

def p_whileblockend(p):
	'''whileblockend : empty'''
	print "goto, "+p[-6][0]
	print "label, "+p[-6][1]

def p_forloop(p):
	'''forloop : FOR scope_marker LEFTPAREN initialization SEMICOLON forexpr_marker for_expr forcheck_marker SEMICOLON increment increment_marker RIGHTPAREN forblock endblock_marker'''

def p_scope_marker(p):
	'''scope_marker : '''
	addscope()

def p_forexpr_marker(p):
	'''forexpr_marker : '''
	l1=createlabel()
	l2=createlabel()
	l3=createlabel()
	l4=createlabel()
	p[0] = [l1, l2, l3, l4]
	print "label, "+l1

def p_forcheck_marker(p):
	'''forcheck_marker : '''
	t = newtemp()
	print "B=, "+t+", 1"
	print "ifgoto, je, "+p[-1]['place']+", "+t+", "+p[-2][1]
	print "goto, "+p[-2][2]
	print "label, "+p[-2][3]	

def p_increment_marker(p):
	'''increment_marker : '''
	print "goto, "+p[-5][0]
	print "label, "+p[-5][1]	
def p_endblock_marker(p):
	'''endblock_marker : '''
	print "goto, "+p[-8][3]
	print "label, "+p[-8][2]
	removescope()

def p_forblock(p):
	'''forblock : LEFTBRACE statements RIGHTBRACE'''

def p_initialization(p):
	'''initialization : assignment
					  | reinitialization'''
def p_reinitialization(p):	
	'''reinitialization : reassignment COMMA reinitialization
					  | reassignment'''


def p_for_expr(p):
	'''for_expr : expression'''
	p[0] = newdict(['type',p[1]['type'],'place',p[1]['place']])

def p_increment(p):
	'''increment : reassignment SEMICOLON increment
				 | reassignment'''

#FunctionDeclarartion
def p_funcarghead(p):
	'''funcarghead : funcargList'''
	this = st['scopes'][len(st['scopes'])-1]
	counter =1
	for var in p[1]:
		if var not in this['vars']:
			new = createtemp(var,this,"UNDEFINED",data={})
			print "args, "+new+", "+str(counter)
			counter = counter +1
		else:
			raise SyntaxError

def p_funcargList(p):
	'''funcargList : ID COMMA funcargList'''
	p[0] = [p[1]] + p[3]


def p_funcargList_base(p):
	'''funcargList : ID'''
	p[0] = [p[1]]

def p_funcargList_empty(p):
	'''funcargList : '''
	p[0] = []


#FUNCTIONNORMAL
def p_funcdecl_normal(p):
	'''funcdecl : FUNCTION ID funcscopedefnormal LEFTPAREN funcarghead RIGHTPAREN funblock endfunc'''
	removescope()

def p_funcscopedefnormal(p):
	'''funcscopedefnormal : '''
	this = st['scopes'][len(st['scopes'])-1]
	p[0]={}
	if ( p[-1] in this['funs']) or (p[-1] in this['vars']):
		print "Function Already Defined"
		raise SyntaxError
	else:
		new = createfun(p[-1])
		labeljmp =	createlabel()
		print "goto, "+labeljmp
		print "label, "+new
		p[0]['label'] = labeljmp
	addscope()

def p_endfunc(p):
	'''endfunc : empty'''
	print "ret"
	print "label, "+p[-5]['label']


#VARIABLEFUNCDECL
def p_funcdecl_vardecl(p):
	'''funcdecl	: VAR ID EQ FUNCTION funcscopedef LEFTPAREN funcarghead RIGHTPAREN funblock SEMICOLON endfuncdecl'''
	removescope()

def p_funblock(p):
	'''funblock : LEFTBRACE statements RIGHTBRACE'''

def p_funcscopedef(p):
	'''funcscopedef : '''
	this = st['scopes'][len(st['scopes'])-1]
	#p[0]={}
	if ( p[-3] in this['funs']) or (p[-3] in this['vars']):
		print "Function Already Defined"
		raise SyntaxError
	else:
		new = createfun(p[-1])
		labeljmp =	createlabel()
		print "goto, "+labeljmp
		print "label, "+new
		#p[0]['label'] = labeljmp
	addscope(p[-3])

def p_endfuncdecl(p):
	'''endfuncdecl : '''
	print "ret"
	print "label, "+p[-6]['label']	

def p_empty(p):
	'''empty : '''

def p_error(p):
	print p
	print("YOU GOT A BUG IN YOUR INPUT, PLEASE CHECK")
	return

parser = yacc.yacc()
toks = []


def read_data(file):
	dir = os.path.dirname(os.path.realpath('__file__'))
	if len(sys.argv)<2:
		print 'No Input file specified'
		sys.exit()
	else:
		filename = dir+'/'+file
		fd = open(filename,'r')
		data=fd.read()
		lexFunc(data,toks)
		input = ""
		for tok in toks:
			if tok.type == "LCOMMENT" or tok.type == "BCOMMENT":
				continue
			input = input + str(tok.value) + " "
		return input

if __name__ == '__main__':
	filename = sys.argv[1]
	data = read_data(filename)
	result = parser.parse(data, lexer)
