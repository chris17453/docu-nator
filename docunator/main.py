import argparse
from pprint import pprint
from .patch import patch
from .parse import parse
from .summarize import summarize
from .helpers import get_python_files, check_files_exist_and_readable




# Parses command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject docstrings into a Python file and create a patch.")
    parser.add_argument("--dir", type=str, help="Path to the directory to patch",default=None)
    parser.add_argument("--file", type=str, help="Path to the Python file to patch")
    parser.add_argument("--temp", type=str, help="location to work with temp files",default="./_temp")
    parser.add_argument("--patch", type=str, help="location to storepatch files",default="./_patch")
    

    args=parser.parse_args()
    
    # get the batch array of files to work
    if args.dir:
        python_files = get_python_files(args.dir)
    elif args.file:
        python_files = [args.file]

    # Validate files before analysing them
    results=check_files_exist_and_readable(python_files)
    err=None
    for file, status in results.items():
        if status==False:
            print(f"Error: File {file} does not exist or is not readable.")
            err=1
    if err!=None:
        exit(1)


    # load up the local LLM
    model_dir="/home/nd/ai/Mistral-7B-Instruct-v0.2"
    doc_sum=summarize(model_dir)
    print(python_files)
    patches=[]
    for file in python_files:
        # Parse the file
        print (f"Working on {file}")
        meta_data=parse(file)
        #pprint(meta_data)
        for func in meta_data:
            print("")
            print("")
            print(func['name'])
            # Generate goc string
            docstring=doc_sum.generate(func['code'])
            func['docstring']=docstring
            print("----------------------------------")
            print(func['code'])
            print("==================================")
            print(func['docstring'])
            print("++++++++++++++++++++++++++++++++++")
            
        # Generate the patches
        patch_file=patch(file,args.temp,args.patch,meta_data)
        patches.append(patch_file)
            

    # Report patched files
    for file in patches:
        print(f"{file}")