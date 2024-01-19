import os
import shutil
import difflib
import uuid

def create_patch(original_file, modified_file, patch_file):
    """Create patch file from two different files
    
    Args:
    original_file (str): The file to be considered as the original one.
        This file is read to get the original lines.
        Mandatory argument.
    modified_file (str): The file to be considered as the modified one.
        This file is read to get the modified lines.
        Mandatory argument.
    patch_file (str): The file where the patch file will be written.
        Mandatory argument.
    
    Returns:
    None: This function does not return any value.
        It only writes the patch file to the given location.
    
    Raises:
    FileNotFoundError: If any of the given files are not found.
    
    Notes:
    This function uses the diff library to find the differences between
    the original and modified files and writes them to a patch file.
    """
    with open(original_file, 'r') as file:
        original_lines = file.readlines()
    with open(modified_file, 'r') as file:
        modified_lines = file.readlines()

    diff = difflib.unified_diff(original_lines, modified_lines, 
                                fromfile=modified_file, tofile=original_file, lineterm='\n')

    with open(patch_file, 'w') as file:
        file.writelines(diff)

def find_function_end(lines, start_line, end_line):
    """Finds the index of the last line of a function definition in a list of lines.
    
    Args:
    lines (List[str]): A list of strings representing the lines of a file.
    start_line (int): The index of the first line of the function definition.
    end_line (int): The index of the first line after the function definition.
    
    Returns:
    int: The index of the last line of the function definition.
    
    Raises:
    ValueError: If the function definition is not found between start_line and end_line.
    
    Notes:
    - The function definition is assumed to start with 'def' followed by a function name and parentheses.
    - The function definition is assumed to end with a ':' or an empty line.
    """
    #print ("Information")
    #print(lines)

    for i in range(start_line, end_line):
        #print(f"LINE: {i}")
        if not lines[i].strip().endswith(',') and not lines[i + 1].lstrip().startswith(('def ','def\t', ' ')):
            return i
    return end_line - 1

def get_indentation(lines, start_line):
    """get_indentation(lines: List[str], start_line: int) -> int or -1
    
    This function determines the indentation level of the code block following the given definition line.
    
    Args:
    lines: A list of strings representing lines of code.
    start_line: The index of the line in the list where the definition line is located.
    
    Returns:
    The number of spaces representing the indentation level of the code block following the definition line.
    
    Raises:
    ValueError if the definition line is not found or the code block following the definition line is not present.
    
    Notes:
    The function searches for the definition line by looking for the string 'def' at the beginning of a line. Once the definition line is found, it searches for the first line following the definition line that contains code (ignoring comments). The indentation level is determined by the number of spaces at the beginning of that line.
    """
    def_line = -1
    inside_def = False
    # Find def line
    for i, line in enumerate(lines[start_line:], start=start_line):
        stripped_line = line.strip()
        if 'def' in stripped_line and stripped_line.startswith('def'):
            def_line = i
            inside_def = True
        # Check for end of def block, ignoring comments
        if inside_def and not stripped_line.startswith("#"):
            if ':' in stripped_line:
                break
    if def_line == -1:
        return -1  # def not found
    # Find the first line after def with code
    for line in lines[i + 1:]:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith("#"):
            return len(line) - len(stripped_line)-1
    return -1  # Code block not found after def


def format_docstring(docstring, indentation):
    """Calculates the sum of two numbers.
    
    Args:
        num1 (float or int): The first number to be added. Required.
        num2 (float or int): The second number to be added. Required.
    
    Returns:
        sum (float or int): The sum of num1 and num2.
    
    Raises:
        TypeError: If num1 or num2 is not a number.
    
    Notes:
        This function does not handle complex numbers.
    """
    indent = ' ' * indentation
    lines=docstring.split("\n")
    output=[]
    for line in lines:
        output.append(f"{indent}"+line)
    return "\n".join(output)+"\n"

def inject_docstring(file_path, docstring_data):
    """
    Injects docstrings from a provided docstring_data list into the corresponding functions
    in the given file_path.
    
    Args:
        file_path (str): The path to the python file to be updated.
        docstring_data (list): A list of dictionaries, each representing a docstring patch.
            Each dictionary should have the following keys:
                - 'start_line': The line number where the docstring starts.
                - 'end_line': The line number where the docstring ends.
                - 'docstring': The docstring text to be injected.
    
    Returns:
        A tuple containing the original lines and the modified lines.
    
    Raises:
        FileNotFoundError: If the provided file_path does not exist.
        SyntaxError: If the provided python file contains syntax errors.
    
    Notes:
        This function assumes that the docstring is located on a new line right before the function definition.
        The docstring is considered to be the lines between the start_line and end_line (inclusive).
    """
    with open(file_path, 'r') as file:
        original_lines = file.readlines()

    modified_lines = original_lines.copy()

    # Sort docstring data by start_line to handle patches in any order
    docstring_data_sorted = sorted(docstring_data, key=lambda x: x['start_line'])
    offset = 0

    for data in docstring_data_sorted:
        if 'docstring' not in data or data['docstring'] is None:
            continue

        # Adjust start_line and end_line according to the current offset
        start_line = data['start_line'] + offset
        end_line = data['end_line'] + offset

        function_end_line = find_function_end(modified_lines, start_line, end_line)
        indentation = get_indentation(modified_lines,start_line)
        print(f"Indent:{indentation}")
        docstring_lines = format_docstring(data['docstring'], indentation)

        # Insert the docstring lines at the adjusted position
        modified_lines[function_end_line + 1:function_end_line + 1] = docstring_lines

        # Update offset based on the number of lines added
        offset += len(docstring_lines)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

    return original_lines, modified_lines

def patch(file,temp_dir,patch_dir,docstring_data):
    """Patch a file and generate a patch file.
    
    Args:
        file (str): The path to the file to be patched.
        temp_dir (str): The directory to store the temporary copy of the file.
        patch_dir (str): The directory to store the generated patch file.
        docstring_data (str): The docstring data to be injected into the file.
    
    Returns:
        None. A patch file will be created in the specified patch directory.
    
    Raises:
        FileNotFoundError: If the original file or the temporary or patch directories do not exist.
        PermissionError: If the original file or the temporary copy of the file do not have write permissions.
    
    Notes:
        This function uses the `uuid` and `os` modules for generating unique IDs and checking file and directory paths.
        It also uses the `shutil` module for copying files and the `inject_docstring` and `create_patch` helper functions.
    """
    original_file = file
    temp_dir = temp_dir
    #print(original_file)

    
    # Generate a unique ID
    unique_id = uuid.uuid4()

    temp_file = os.path.join(temp_dir, os.path.basename(original_file))
    patch_file = os.path.join(patch_dir, str(unique_id) + os.path.basename(original_file) + '.patch')

    # Ensure temporary directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Ensure patch directory exists
    if not os.path.exists(patch_dir):
        os.makedirs(patch_dir)

    # Copy original file to temporary directory
    shutil.copy2(original_file, temp_file)

    # Inject docstrings
    inject_docstring(temp_file, docstring_data)

    # Create a patch file
    create_patch(original_file, temp_file, patch_file)
    print(f"Patch file created: {patch_file}")
