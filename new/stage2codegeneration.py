import sys
import pprint
import copy
import re

operators = ["=", "~", "!", "&", "+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>", "ifgoto", "&", "pointer", "address", "goto"]
non_operators = ['param', 'call', 'ret', 'label', 'print']
rel_operators = ['jl', 'jg', 'je', 'jle', 'jge']

language = operators + non_operators + rel_operators
allvariables=[]
variablelist={}
labels=[1]
registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']
registerlist = {}
for a in registers:
	registerlist[a]={'state':"empty",'temp':-1}

label_flag = {}
label_flag['state'] = False

def fetchreg(var,op,st):

	variablelist[var]['location']='register'
	#SomeRegisterEmpty
	for reg in registerlist:
		if registerlist[reg]['state']=='empty':
			registerlist[reg]['state']= 'filled' 
			registerlist[reg]['temp']=var
			variablelist[var]['reg']=reg
			return reg

	#Noregisterempty
	Next_Use=-1
	longest_unused_reg=0
	longest_unused_var=''
	for reg in registerlist:
		a = registerlist[reg]['temp']
		if a not in st:
			longest_unused_reg = reg
			longest_unused_var = a
			break

		if st[a]['state'] == 'dead':
			longest_unused_reg = reg
			longest_unused_var = a
			break

		if Next_Use < st[a]['next_use']:
			Next_Use=st[a]['next_use']
			longest_unused_reg = reg
			longest_unused_var = a

	print("\tmovl "+str('%'+longest_unused_reg) +", "+str(longest_unused_var))
	registerlist[longest_unused_reg]['state']='filled'
	registerlist[longest_unused_reg]['temp']=longest_unused_var		
	variablelist[var]['reg']=longest_unused_reg
	return	longest_unused_reg				


def assembly(block,blockvariables,Linesymbols,index):
	operator = block[index][0]
	#print(operator)
	#print(variablelist[blockvariables[index][0]])

	not_good_ops = ['/', '%', 'print', '>>', '<<', 'pointer', 'address']
	if operator not in not_good_ops:
		
		varcount = 0
		for var in blockvariables[index]:
			varcount+=1
			i = blockvariables[index].index(var)
			if variablelist[var]['location'] != 'register':
				tempreg = fetchreg(var,operator,Linesymbols[index])
				if len(blockvariables[index])>1:
					print "\tmovl "+var+", %"+tempreg
			else:
				tempreg = variablelist[var]['reg']
			blockvariables[index][i]="%"+tempreg

		if operator == '=':
			#print(operator)
			t = block[index][len(block[index])-1]
			try:
				userInput = int(t)
			except:
				isnumber = False
			else:
				isnumber = True
			if isnumber:
				t = '$'+t
			else:
				t = blockvariables[index][len(block[index])-1]

			print "\tmovl "+t+", "+blockvariables[index][0]
			return


		if operator ==  '+':
			print "\taddl "+blockvariables[index][1]+", "+blockvariables[index][0]
			return
        if operator == '*':
         	print "\timul "+blockvariables[index][1]+", "+blockvariables[index][0]
         	return
        #print(operator)
        if operator == '-':
        	#print('yes')
         	print "\tsubl "+blockvariables[index][1]+", "+blockvariables[index][0]
         	return
        if operator == '<<':
         	print "\tshl "+blockvariables[index][0]+", "+blockvariables[index][1]
         	return
        if operator == '>>':
         	print "\tshr "+blockvariables[index][0]+", "+blockvariables[index][1]
         	return
        if operator == 'ifgoto':
         	print "\tcmp "+blockvariables[index][1]+", "+blockvariables[index][0]
         	blockindex = labels.index(int(block[index][4]))
         	print "\t"+block[index][1]+" LABEL"+str(blockindex+1)
         	return
        if operator == 'goto':
         	blockindex = labels.index(int(block[index][1]))
         	print "\tjmp LABEL"+str(blockindex+1)
         	return
        if operator == 'call':
         	fun = block[index][1]
         	#print(fun)
         	for reg in registerlist:
         		if registerlist[reg]['state']!='empty':
         			tempvar = registerlist[reg]['temp']
         			print '\tmovl %'+reg+', '+tempvar
         			registerlist[reg]['state']='empty'
         			variablelist[tempvar]['location']='memory'
         	print "\tcall "+fun
         	return
        if operator == 'label':
         	print block[index][1]+":"
         	label_flag['state']=True
         	return
        if operator == "ret":
         	for reg in registerlist:
         		if registerlist[reg]['state']!='empty':
         			tempvar=registerlist[reg]['temp']
         			variablelist[tempvar]['location']='memory'
         			registerlist[reg]['state']='empty'
         			print '\tmovl %'+reg+', '+tempvar

         	if label_flag['state']==True:
         		print '\tret'
         	else:
         		print '\tcall end_label'
         	return
        if operator == '|':
         	print '\torl '+blockvariables[index][1]+', '+blockvariables[index][0]
         	return
        if operator == '&':
         	print '\tandl '+blockvariables[index][1]+', '+blockvariables[index][0]
         	return
        if operator == '^':
         	print '\txorl '+blockvariables[index][1]+', '+blockvariables[index][0]
         	return
        if operator == '!':
         	print '\tnotl '+blockvariables[index][0]
         	return
        if operator == '~':
         	print '\tnegl '+blockvariables[index][0]
         	return
	#print("eddd")
		#return
	#print("edf")
	
	
	if operator == 'print':
		#print("yes")
		toprint = blockvariables[index][0]
		if variablelist[toprint]['location']=='register':
			reg =  variablelist[toprint]['reg']
			print '\tmovl %'+reg+', '+toprint
			variablelist[toprint]['location']='memory'
			registerlist[reg]['state']='empty'
		for reg in registers:
			if registerlist[reg]['state']!='empty':
				tempvar=registerlist[reg]['temp']
				variablelist[tempvar]['location']='memory'
				print '\tmovl %'+reg+', '+tempvar
				registerlist[reg]['state']='empty'
		print '\tpushl '+toprint
		print  '\tcall printIntNumber'
		print '\tpopl '+toprint
		return

	if operator == '<<' or operator == '>>':
		no = blockvariables[index][0]
		toshift = blockvariables[index][1]
		if variablelist[no]['location']=='register':
			tempreg = variablelist[no]['reg']
			print '\tmovl %'+tempreg+', '+no
			variablelist[no]['location']='memory'
			registerlist[tempreg]['state']='empty'
		if variablelist[toshift]['location']=='register':
			tempreg = variablelist[toshift]['reg']
			print '\tmovl %'+tempreg+', '+toshift
			variablelist[toshift]['location']='memory'
			registerlist[tempreg]['state']='empty'
		req_regs = ['eax','ecx']
		for reg in req_regs:
			if registerlist[reg]['state']!='empty':
				tempvar = registerlist[reg]['temp']
				print '\tmovl %'+reg+', '+tempvar
				variablelist[tempvar]['location']='memory'

		print '\tmovl '+no+', %eax'
		registerlist['eax']['state']='filled'
		registerlist['eax']['temp']=no
		variablelist[no]['location']='register'
		variablelist[no]['reg']='eax'

		print '\tmovl '+toshift+', %ecx'
		registerlist['ecx']['state']='filled'
		registerlist['ecx']['temp']=toshft
		variablelist[toshift]['location']='register'
		variablelist[toshift]['reg']='ecx'

		if operator == '<<':
			print '\tshll %cl %eax'
		else:
			print '\tshrl %cl %eax'
		return
    		
	if operator=='pointer':
		t1 = blockvariables[index][0]
		t2 = blockvariables[index][1]

		for reg in registerlist:
			if registerlist[reg]['state']!='empty':
				tempvar = registerlist[reg]['temp']
				print '\tmovl %'+reg+', '+tempvar
				variablelist[tempvar]['location']='memory'
				registerlist[reg]['state'] = 'empty'

		newreg = fetchreg(t1,operator,Linesymbols[index])
		registerlist[newreg]['state']='filled'
		registerlist[newreg]['temp']=t1
		variablelist[t1]['location']='register'
		variablelist[t1]['reg']= newreg

		print '\tmovl ('+t2+'), %'+newreg
		print '\tmovl (%'+newreg+'), %'+newreg
		return


	if operator == 'address':
		t1 = blockvariables[index][0]
		newreg = fetchreg(t1,operator,Linesymbols[index])
		registerlist[newreg]['state']='filled'
		registerlist[newreg]['temp']=t1
		variablelist[t1]['location']='register'
		variablelist[t1]['reg']= newreg

		t2 =  blockvariables[index][1]
		print '\tmovl $('+t2+'), %'+newreg
		return
	
	if operator == '/' or operator == '%':
		#print(blockvariables[index])
		dst = blockvariables[index][0]
		src = blockvariables[index][1]
		#print(dst)
		backupregs = ['eax','ebx','ecx']
		for reg in backupregs:
			if registerlist[reg]['state'] == 'filled':
				tempvar = registerlist[reg]['temp']
				print '\tmovl %'+reg+", "+tempvar
				variablelist[tempvar]['location']='memory'
		print "\tmovl $0, %edx"

		if variablelist[dst]['location']=='memory':
			print "\tmovl "+dst+", %eax"
		else:
			tempreg = variablelist[dst]['reg']
			print "\tmovl %"+tempreg+", %eax"
			registerlist[tempreg]['state']= 'empty'

		if variablelist[src]['location']=='memory':
			print "\tmovl "+src+", %ebx"
		else:
			tempreg = variablelist[src]['reg']
			print "\tmovl %"+tempreg+", %ebx"
			registerlist[tempreg]['state']= 'empty'

		variablelist[src]['location']='register'
		variablelist[src]['reg']='ebx'
		registerlist['ebx']['state']='filled'
		registerlist['ebx']['temp']= src


		if operator == '/':
			registerlist['edx']['state']='empty'
			variablelist[dst]['location']='register'
			variablelist[dst]['reg']='eax'
			registerlist['eax']['state']='filled'
			registerlist['eax']['temp']= dst

		else:
			registerlist['edx']['state']='filled'
			variablelist[dst]['location']='register'
			variablelist[dst]['reg']='edx'
			registerlist['edx']['temp']= dst
			registerlist['eax']['state']='empty'

		print "\tdivl %ebx"
		return

def process(block,blockvariables):
	varlist = []
	for a in blockvariables:
		for b in a:
			if b not in varlist:
				varlist.append(b)
	
	for var in varlist:
		variable ={}
		variable['location']='memory'
		variable['reg']=-1
		variablelist[var]=variable

	#SymbolTable
	#print(block)
	#print(varlist)
	#print(blockvariables)
	symbols={}
	for temp in varlist:
		temp_obj= {'state':'dead','last_use':-1,'next_use':-1}
		symbols[temp]=temp_obj


	#print(len(symbols))
	Linesymbols = [symbols]
	for line in reversed(block):
		symbols=copy.deepcopy(symbols)
		index = block.index(line)
		if len(blockvariables[index])==0:
			continue
		dst = blockvariables[index][0]
		if dst[0]=='$':
			if symbols[dst]['state']!='dead':
				symbols[dst]['state']='dead'
		temp_count=1
		while temp_count < len(blockvariables[index]):
			src = blockvariables[index][temp_count]
			if src[0]=='$':
				if(symbols[src]['state']=='dead'):
					symbols[src]['state']='live'
					symbols[src]['next_use']=index
					symbols[src]['last_use']=index
				else:
					symbols[src]['next_use']=index
			temp_count+=1
		Linesymbols.insert(0,symbols)
		#print(symbols)
		#print('\n')

	#print(Linesymbols)
	for line in block:
		index = block.index(line)
		#print(line)
		assembly(block,blockvariables,Linesymbols,index)



if __name__ == '__main__':
	input = './' + sys.argv[1]
	with open(input,'rb') as file:
		inputfile = file.readlines()

	#print(inputfile)
	splitted_code = []
	for line in inputfile:
		t = line.split(", ")
		t[len(t)-1]=t[len(t)-1][:-1]
		splitted_code.append(t)
		#print(t)

	#print(splitted_code)
	#Array_Definitons_Not_Removed
	#Remaining


	#Finding Labels
	count =1
	for line in splitted_code:
		if count !=1:
			if line[0] == "ifgoto":
				labels.append(int(line[4]))
				if count + 1 <= len(splitted_code):
					labels.append(count+1)
			elif line[0]=="call":
				if count+1 <= len(splitted_code):
					labels.append(count+1)
			elif line[0] == "goto":
				labels.append(int(line[1]))
			elif line[0] == "label":
				labels.append(count)
		count=count+1
			
	#print(labels)
	#Finding Blocks
	block=[splitted_code[0]]
	Blocks=[]
	count=0
	for line in splitted_code:
		count=count+1
		if count == 1:
			continue
		else:
			if count in labels:
				Blocks.append(block)
				block = [line]
			else:
				block.append(line)
	Blocks.append(block)
	BlockListVariables=[]
	#print(Blocks)
	#Taking all variables in allvariables
	nonvar= ['label','call']
	for oneblock in Blocks:
		thisblockvariables=[]
		for line in oneblock:
			thislinevariables=[]
			if line[0] in nonvar:
				thisblockvariables.append(thislinevariables)	
				continue
			for token in line:
				if token not in language :
					try:
						u = int(token)
					except:
						isno = False
					else:
						isno = True
					if not isno:
						thislinevariables.append(token)
						if token not in allvariables:
							allvariables.append(token)
			thisblockvariables.append(thislinevariables)
		BlockListVariables.append(thisblockvariables)
 
	#print(BlockListVariables)
    #Assembly_headers
	print '.section .text'
	print '\t.global _start'


	count=0
	for oneblock in Blocks:
		if count ==0:
			print '_start:'
		elif oneblock[0][0]!='label':
			print "LABEL"+str(count)+":"
		process(oneblock,BlockListVariables[count])
		count = count + 1
		print ""




	a = 'end_label:\n\
	movl $1, %eax\n\
	movl $0, %ebx\n\
	int $0x80\n\
	'

	print ""+a
	a = 'printIntNumber:\n\
	movl 4(%esp), %ecx\n\
	cmpl $0, %ecx\n\
	jge positive_part\n\
	notl %ecx\n\
	inc %ecx\n\
	movl %ecx, %edi\n\
	movl $45, %eax\n\
	pushl   %eax\n\
	movl $4, %eax\n\
	movl $1, %ebx\n\
	movl %esp, %ecx\n\
	movl $1, %edx\n\
	int $0x80\n\
	popl %eax\n\
	movl %edi, %ecx\n\
positive_part:\n\
movl %ecx, %eax\n\
	movl %esp, %esi\n\
iter_labl:\n\
	cdq\n\
	movl $10, %ebx\n\
	idivl %ebx\n\
	pushl %edx\n\
	cmpl $0, %eax\n\
	jne iter_labl\n\
	jmp print_num\n\
	\n\
print_num:\n\
	popl %edx\n\
	addl $48, %edx\n\
	pushl %edx\n\
	movl $4, %eax\n\
	movl $1, %ebx\n\
	movl %esp, %ecx\n\
	movl $1, %edx\n\
	int $0x80\n\
	popl %edx\n\
	cmp %esp, %esi\n\
	jne print_num\n\
	ret  \n\
	EndPrintNum:\n'
	print a

    

    #Section_For_Data
	print '.section .data'
	for word in allvariables:
	    print word+":"
	    print "\t.long 0"
	print 'type:'
	print '\t.ascii "HELLO %d HELLO\\n\\0"'