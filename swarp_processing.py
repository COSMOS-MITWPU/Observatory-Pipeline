
def make_swarp_command(swarpConfigFile, procFolder, how_do_you_call_swarp): 
    swarpFileList = os.path.join(procFolder, 'swarpFileList.txt')
    new_file_names = []
    
    # extracting the list and making the command
    with open(os.path.join(procFolder, 'swarpFileList.txt'), 'r+') as f:
        file_names = f.readlines()
        
    for i in file_names[:]:
        new_file_names.append(i.strip('\n'))

    # merging the list into a single string
    input_files = ' '.join(new_file_names)
    command = f'{how_do_you_call_swarp} {input_files} -c {swarpConfigFile}'
    with open('./new.txt', 'w') as f:
        f.write(command)
        
    return command

def swarpConfig(dataFolder,sciList):
    swarpConfigFile = os.path.join(dataFolder, 'stack.swarp')

    f = open(swarpFileList, 'w')
    for i in range(numSciFiles):
        f.write(os.path.join(procFolder, 'a'+fileList[i]+'.proc.cr.fits\n'))
    f.close()
    
    try:
        # Make a text file listing the images to be stacked to feed into swarp
        command = make_swarp_command(swarpConfigFile, procFolder, 'swarp')
        print("Executing command: %s" % command)
        print(command)
        subprocess.run(command, shell=True)
    except:
        print('trying another way to call SWarp')
        command = make_swarp_command(swarpConfigFile, procFolder, 'SWarp')
        print("Executing command: %s" % command)
        print(command)
        subprocess.run(command, shell=True)
    print(os.getcwd())


swarpConfig(dataFolder,sciList)