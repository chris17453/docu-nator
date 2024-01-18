import os


def get_python_files(directory):
    '''Gets a list of all Python files in the given directory and its subdirectories.
    
    Args:
        directory (str): The directory to search for Python files.
    
    Returns:
        list: A list of absolute paths to all Python files in the given directory and its subdirectories.
    
    Raises:
        None
    
    Notes:
        This function uses the os.walk() function to recursively traverse the directory tree and find all files with the .py extension.
    '''
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_files_exist_and_readable(files):
    '''Checks if all given files exist and are readable.
    
    Args:
        files (list): List of file paths to check.
    
    Returns:
        dict: A dictionary with file paths as keys and boolean values indicating
             whether the file exists and is readable.
    
    Raises:
        None
    
    Notes:
        This function does not handle errors when a file does not exist or is not readable.
        It simply returns False for those files.
    '''
    result = {}
    for file in files:
        result[file] = os.path.isfile(file) and os.access(file, os.R_OK)

    return result