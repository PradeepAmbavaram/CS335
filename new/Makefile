all:	make raw test1 test2  test3 test4 test5  test6  test7 test8 test9  

raw:
	python stage1parsing.py raw.js > raw
	python stage2codegeneration.py raw > raw.s
	as --32 raw.s -o raw.o
	ld -m elf_i386 raw.o -o oraw
	./oraw

test1:
	python stage1parsing.py testcases/test1.js > test1
	python stage2codegeneration.py test1 > test1.s
	as --32 test1.s -o test1.o
	ld -m elf_i386 test1.o -o otest1 
	./otest1

test2:
	python stage1parsing.py testcases/test2.js > test2
	python stage2codegeneration.py test2 > test2.s
	as --32 test2.s -o test2.o
	ld -m elf_i386 test2.o -o otest2 
	./otest2
test3:
	python stage1parsing.py testcases/test3.js > test3
	python stage2codegeneration.py test3 > test3.s
	as --32 test3.s -o test3.o
	ld -m elf_i386 test3.o -o otest3 
	./otest3
test4:
	python stage1parsing.py testcases/test4.js > test4
	python stage2codegeneration.py test4 > test4.s
	as --32 test4.s -o test4.o
	ld -m elf_i386 test4.o -o otest4 
	./otest4
test5:
	python stage1parsing.py testcases/test5.js > test5
	python stage2codegeneration.py test5 > test5.s
	as --32 test5.s -o test5.o
	ld -m elf_i386 test5.o -o otest5 
	./otest5
test6:
	python stage1parsing.py testcases/test6.js > test6
	python stage2codegeneration.py test6 > test6.s
	as --32 test6.s -o test6.o
	ld -m elf_i386 test6.o -o otest6 
	./otest6
test7:
	python stage1parsing.py testcases/test7.js > test7
	python stage2codegeneration.py test7 > test7.s
	as --32 test7.s -o test7.o
	ld -m elf_i386 test7.o -o otest7 
	./otest7
test8:
	python stage1parsing.py testcases/test8.js > test8
	python stage2codegeneration.py test8 > test8.s
	as --32 test8.s -o test8.o
	ld -m elf_i386 test8.o -o otest8 
	./otest8
test9:
	python stage1parsing.py testcases/test9.js > test9
	python stage2codegeneration.py test9 > test9.s
	as --32 test9.s -o test9.o
	ld -m elf_i386 test9.o -o otest9 
	./otest9

clean: 
	remove test* ,test*.o,test*.s,otest*