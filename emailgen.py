"""
 "  Author:	Damian Behymer
 "  Created:	2018-04-10
 "  Modified:	2018-11-29
 "
 "  This code replaces ##-delimited segments from a template file
 "  with corresponding segments from a text file and spits out
 "  a formatted html newsletter.
 "
 "  Usage: python emailgen.py [optional filename arguments]
 "  
 "  optional arguments:
 "    -t (template file, defaults to template.html)
 "    -e (email text file, defaults to emailtext.txt)
 "    -o (output html file, defaults to current date YYYY-MM-DD.html)
 "
"""
from datetime import date
from sys import argv
import sys

outFileName = str(date.today()) + ".html"
templateFileName = "template.html"
emailtextFileName = "emailtext.txt"

"""
 "  Replaces template, emailtext, and output filenames based on -t,
 "  -e, and -o arguments, and prints usage if arguments are not in
 "  the expected format.
"""
def processArgs():
	global outFileName, templateFileName, emailtextFileName
	if len(argv) % 2 == 0:
		printUsage()
	i = 1
	while True:
		if i >= len(argv):
			break
		if argv[i] == "-t":
			templateFileName = argv[i+1]
			i += 2
		elif argv[i] == "-e":
			emailtextFileName = argv[i+1]
			i += 2
		elif argv[i] == "-o":
			outFileName = argv[i+1]
			i += 2
		else:
			printUsage()


"""
 "  Prints usage of the command.
"""
def printUsage():
	s = "Usage: python emailgen.py [optional filename arguments]\n\n"
	s += "optional arguments:\n"
	s += "  -t (template file, defaults to template.html)\n"
	s += "  -e (email text file, defaults to emailtext.txt)\n"
	s += "  -o (output html file, defaults to current date YYYY-MM-DD.html)\n"
	print(s)
	sys.exit(-1)


"""
 "  Scans text from input and writes to output until it finds a
 "  ##-delimited keyword, returns that keyword and the inputText
 "  cursor positioned after the closing ##.
"""
def readWriteToNext(inputText, outputText):
	while True:
		nextchar = inputText.read(1)
		if nextchar == "":
			return ""
		elif nextchar == "\\":
			nextchar = inputText.read(1)
			outputText.write(nextchar)
		elif nextchar == "#":
			if inputText.read(1) == "#":
				return getWord(inputText)
			else:
				inputText.seek(inputText.tell() - 1, 0)
				outputText.write(nextchar)
		else:
			outputText.write(nextchar)


"""
 "  Scans characters from 'text' and looks for a ##-delimited
 "  keyword. Returns the first keyword it finds, or an empty
 "  string if no such keyword is found. Positions cursor at 
 "  the end of the closing ##.
"""
def readToNext(text):
	while True:
		nextchar = text.read(1)
		if nextchar == "":
			return ""
		elif nextchar == "\\":
			text.seek(1, 1)
		elif nextchar == "#":
			if text.read(1) == "#":
				return getWord(text)
			else:
				text.seek(text.tell() - 1, 0)


"""
 "  goes through emailtext.txt looking for the proper text
 "  to be inserted into the template, returns that text.
 "  depending on varname, it may HTML-ify the text in
 "  emailtext.txt or perform other operations on it, as in
 "  EMAILTEXT and TLDRLIST.
"""
def getText(varname, whitespace = ""):
	text = open(emailtextFileName, "r")
	while True:
		word = readToNext(text)
		if word == varname:
			break
		if word == "":
			return ""
	result = ""
	while True:
		nextchar = text.read(1)
		if nextchar == "":
			break
		elif nextchar == "\\":
			text.seek(text.tell() + 1, 0)

		elif nextchar == "#":
			if text.read(1) == "#":
				break
			else:
				text.seek(text.tell() - 1, 0)
		result += nextchar
	text.close()
	if varname[-2:] == "-P":
		return paragraphify(result, whitespace)
	elif varname[-2:] == "-L":
		return listify(result, whitespace)
	return result.strip()

	
"""
 "  Assumes the cursor in 'text' is positioned after the first
 "  ## delimiter in a pair. This function reads until the next
 "  ## and returns the intermediate sequence.
"""
def getWord(text):
	word = ""
	while True:
		nextchar = text.read(1)
		if nextchar == "":
			break
		if nextchar == "#":
			if text.read(1) == "#":
				break
			else:
				text.seek(text.tell() - 1, 0)

		word += nextchar
	return word


"""
 "  Transforms an input string into an HTML formatted sequence
 "  of paragraphs based on line break characters.
"""
def paragraphify(text, whitespace = ""):
	first = True
	result = ""
	array = text.split('\n');
	for n in array:
		if n == "":
			continue;
		elif n[0] == "<" and n[len(n)-1] == ">":
			if first:
				result += n + "\n"
				first = False
			else:
				result += whitespace + n + "\n"
		elif first:
			result += "<p>" + n + "</p>\n"
			first = False
		else:
			result += whitespace + "<p>" + n + "</p>\n"
	return result


"""
 "  Transforms an input string into an HTML formatted sequence
 "  of <li> items. Assumes that all list items begin with 
 "  " - " and end in a line break.
"""
def listify(text, whitespace = ""):
	first = True
	result = ""
	array = text.split(" - ")
	for n in array:
		nn = n.strip()
		if (nn == ""):
			continue
		elif first:
			result += "<li>" + nn.strip() + "</li>\n"
			first = False
		else:
			result += whitespace + "<li>" + nn.strip() + "</li>\n"
	return result


"""
 "  Assuming the cursor in "text" is positioned after the
 "  closing ## of a delimited keyword, searches backwards
 "  and returns the whitespace between the last endline and
 "  the opening ## for purposes of nicely formatted html.
"""
def findWhiteSpace(text):
	pos = text.tell()
	text.seek(text.tell() - 1, 0)
	foundSpace = False

	result = ""
	i = 0
	while True:
		#i += 1
		#if i > 20:
		#	break
		#print(text.read(10))
		#text.seek(text.tell() - 10, 0)
		#print(text.tell())
		text.seek(text.tell() - 1)
		if text.tell() == 0:
			break;
		nextchar = text.read(1)
		if nextchar == "\n" or nextchar == "":
			break
		elif nextchar.isspace():
			foundSpace = True
			result = nextchar + result
			text.seek(text.tell() - 1, 0)
		elif foundSpace == False:
			text.seek(text.tell() - 1, 0)
			continue
		else:
			text.seek(pos, 0)
			return ""
	text.seek(pos, 0)
	return result



if len(argv) > 1:
	processArgs()

"""
 "  Iterates through characters of template.html, writes
 "  them to YYYY-MM-DD.html, until it gets to a ##-delimited
 "  sequence at which point it looks for the correct text to
 "  copy from emailtext.txt and pastes it into the new html
 "  file.
"""
email = open(templateFileName, "r")
email_output = open(outFileName, "w")

while True:
	# grab the next tag
	word = readWriteToNext(email, email_output)
	whitespace = findWhiteSpace(email)
	if word == "":
		break;

	# handle OPT tags
	if len(word) > 3 and word[0:4] == "OPT-":	
		substitution = getText(word[4:], whitespace)
		if substitution == "":
			# skip over all text until closing OPT tag
			while True:
				checkEndString = readToNext(email)
				if checkEndString == word or checkEndString == "":
					break
		else:
			continue
	
	substitution = getText(word, whitespace)
	email_output.write(substitution)

email.close()
email_output.close()



