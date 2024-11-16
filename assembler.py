import sys

'''

This is a very basic assembler which takes a text file as input and ouputs the binary version to another file
supports line comments prefixed with '/', it also ignores anything past the instruction

it does not support any error handling besides basic syntax

I believe it is only python3 compatible since it uses match statements

to use:
	python3 assembler.py [input file] [output file]

'''

labels = {
	"start": 0,
}

opcodes = {
	"halt": 0,
	"add" : 1,
	"sub" : 2,
	"and" : 3,
	"or"  : 4,
	"lsl" : 5,
	"mov" : 6,
	"cmp" : 7,
	"b"   : 8,
	"be"  : 9,
	"bl"  : 10,
	"bg"  : 11,
	"lw"  : 12,
	"sw"  : 13,
	"nop" : 14
}

registers = {
	"r0" : 0,
	"pc" : 0,
	"sp" : 1,
	"r1" : 1,
	"r2" : 2,
	"r3" : 3,
	"r4" : 4,
	"r5" : 5,
	"r6" : 6,
	"r7" : 7,
	"rr" : 7
}

# read file from command line argument
filename = sys.argv[1]
print("Processing " + filename)
f = open(filename, "r")

outputfile = sys.argv[2]
print("Outputing to " + outputfile)
of = open(outputfile, "w")

lineNumber = 0
# parse file initially to find any labels, this is not efficient but it doesn't matter for the size of programs
# i'm creating
for line in f:
	words = line.split()
	if(line.strip() and words[0][0] != '/'): # only do if not an empty line or comment
		if(opcodes.get(words[0], -1) == -1): # if first word in line is not opcode then it must be a label
			labels.update({words[0] : lineNumber})
		lineNumber+=1

f.seek(0)

# read file line by line and process
lineNumber = 0
for line in f:
	words = line.split()
	if(line.strip() and words[0][0] != '/'): # only do if not an empty line or comment
		if(opcodes.get(words[0], -1) == -1): # if first word in line is not opcode then it must be a label
			opcode = words[1] # opcode will be next word
			i = 1 # index of opcode word
		else:
			opcode = words[0]
			i = 0 # index of opcode word

		# get numerical opcode
		opcode = opcodes.get(opcode, -1)
		if(opcode == -1):
			print("OP-CODE not found instruction #: " + lineNumber)
			exit()

		if(opcode == 0 or opcode == 14 or opcode == 15):
			print("{:016b}".format(opcode<<12))

		# Handles add through cmp, and Memory Instructions
		elif((opcode >= 0 and opcode <= 7) or opcode >= 12):
			# get reg1
			reg1 = registers.get(words[i+1], -1)
			if(reg1 == -1):
				print("Invalid Register instruction #: " + lineNumber)
				exit()
			# handle I-type
			if(words[i+2][0] == '#'):
				immediate = int(words[i+2][1:len(words[i+2])])
				print("{:04b}_1_{:03b}_{:08b}".format(opcode,reg1,immediate))
			# handle R-type with offset
			elif(words[i+2][0] == '('):
				close_index = words[i+2].find(')')
				if(close_index == -1):
					print("Missing ) instruction #: " + lineNumber)
					exit()
				offset = int(words[i+2][1:close_index])
				reg2 = words[i+2][close_index+1:len(words[i+2])]
				reg2 = registers.get(reg2, -1)
				if(reg2 == -1):
					print("Invalid Register instruction #: " + lineNumber)
					exit()
				print("{:04b}_0_{:03b}_{:03b}_{:05b}".format(opcode,reg1,reg2,offset))
			else:
				reg2 = words[i+2][0:len(words[i+2])]
				reg2 = registers.get(reg2, -1)
				if(reg2 == -1):
					print("Invalid Register instruction #: " + lineNumber)
					exit()
				print("{:04b}_0_{:03b}_{:03b}_00000".format(opcode,reg1,reg2))

		# Handle Branch Instructions
		#elif(opcode >= 8 and opcode <= 11):
		else:
			if(words[i+1][0] == '('):
				close_index = words[i+1].find(')')
				if(close_index == -1):
					print("Missing ) instruction #: " + lineNumber)
					exit()
				immediate = int(words[i+1][1:close_index])
				reg1 = words[i+1][close_index+1:len(words[i+1])]
				reg1 = registers.get(reg1, -1)
				if(reg1 == -1):
					print("Invalid Register instruction #: " + lineNumber)
					exit()
				print("{:04b}_1_{:03b}_{:08b}".format(opcode,reg1,immediate))
			elif(words[i+1][0] == '#'):
				address = words[i+1][1:len(words[i+1])]
				if(labels.get(address, -1) == -1):
					address = int(address)
				else:
					address = labels.get(address)
				print("{:04b}_0_{:011b}".format(opcode,address))
			else:
				reg1 = words[i+1]
				reg1 = registers.get(reg1, -1)
				if(reg1 == -1):
					print("Invalid Register instruction #: " + lineNumber)
					exit()
				print("{:04b}_1_{:03b}_{:08b}".format(opcode,reg1,0))

		# only update line number if instruction is present
		lineNumber+=1 

print(labels)
