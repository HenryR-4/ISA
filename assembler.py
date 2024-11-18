import sys

'''
This is a very basic assembler which takes a text file as input and ouputs the binary version to another file

supports line comments prefixed with '/', it also ignores anything past the instruction

supports labels, so long as they are on the same line as an instruction

it does not support any error handling besides very basic syntax

it supports a optional data section at the top, use a tag called "start" at the program
entry point if you include data otherwise it is not required

first line of the output will be a branch to the address of the start tag

to use:
	python3 assembler.py [input file] [output file]

'''

labels = {
	"start": 1,
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

program_str = ""

lineNumber = 1 # start line number at 1 because first instruction will be inserted after  
# parse file initially to find any labels, this is not efficient but it doesn't matter for the size of programs
# i'm creating
for line in f:
	words = line.split()
	if(line.strip() and words[0][0] != '/'): # only do if not an empty line or comment
		if(opcodes.get(words[0], -1) == -1 and not words[0].lstrip('-').isnumeric()): # if first word in line is not opcode and isn't a number then it must be a label
			labels.update({words[0] : lineNumber})
		lineNumber+=1

f.seek(0)

# read file line by line and process
lineNumber = 1 # start line number at 1 because first instruction will be inserted after  
for line in f:
	words = line.split()
	if(line.strip() and words[0][0] != '/'): # only do if not an empty line or comment
		if(labels.get(words[0], -1) != -1): # if first word in line is a label
			opcode = words[1] # opcode will be next word
			i = 1 # index of opcode word
		else:
			opcode = words[0]
			i = 0 # index of opcode word

		if(lineNumber >= labels.get("start")):
			# get numerical opcode
			opcode = opcodes.get(opcode, -1)
			if(opcode == -1):
				print("OP-CODE not found instruction #: " + lineNumber)
				exit()

			if(opcode == 0 or opcode == 14 or opcode == 15):
				program_str += "{:016b}\n".format(opcode<<12)

			# Handles add through cmp, and Memory Instructions
			elif((opcode >= 0 and opcode <= 7) or opcode >= 12):
				# get reg1
				reg1 = registers.get(words[i+1], -1)
				if(reg1 == -1):
					print("Invalid Register instruction #: " + lineNumber)
					exit()
				# handle I-type
				if(words[i+2][0] == '#'):
					immediate = words[i+2][1:len(words[i+2])]
					if(labels.get(immediate, -1) == -1):
						immediate = int(immediate)
					else:
						immediate = labels.get(immediate)
					if(immediate < 0):
						immediate = immediate & 0x00FF 
					program_str += "{:04b}_1_{:03b}_{:08b}\n".format(opcode,reg1,immediate)

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
					if(offset < 0):
						offset = offset & 0x001F
					program_str += "{:04b}_0_{:03b}_{:03b}_{:05b}\n".format(opcode,reg1,reg2,offset)
				else:
					reg2 = words[i+2][0:len(words[i+2])]
					reg2 = registers.get(reg2, -1)
					if(reg2 == -1):
						print("Invalid Register instruction #: " + lineNumber)
						exit()
					program_str += "{:04b}_0_{:03b}_{:03b}_00000\n".format(opcode,reg1,reg2)

			# Handle Branch Instructions
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
					if(immediate < 0):
						immediate = immediate & 0x00FF
					program_str += "{:04b}_1_{:03b}_{:08b}\n".format(opcode,reg1,immediate)
				elif(words[i+1][0] == '#'):
					address = words[i+1][1:len(words[i+1])]
					if(labels.get(address, -1) == -1):
						address = int(address)
					else:
						address = labels.get(address)
					program_str += "{:04b}_0_{:011b}\n".format(opcode,address)
				else:
					reg1 = words[i+1]
					reg1 = registers.get(reg1, -1)
					if(reg1 == -1):
						print("Invalid Register instruction #: " + lineNumber)
						exit()
					program_str += "{:04b}_1_{:03b}_{:08b}\n".format(opcode,reg1,0)
		else:
			opcode = int(opcode)
			if(opcode < 0):
				opcode = opcode & 0xFFFF
			program_str += "{:016b}\n".format(int(opcode))

		# only update line number if instruction is present
		lineNumber+=1 

print(labels)
program_str = "1000_0_{:011b}\n".format(labels.get("start")) + program_str
print(program_str)
of.write(program_str)
