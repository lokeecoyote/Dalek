import dalek as Dalek


kai = Dalek.Dalek()
while True:
	command = raw_input("command:")
	kai.doCommand(command)