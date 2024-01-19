import ast
from pprint import pprint

class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.data={'root':{}}
        self.defined_classes = set()
        self.defined_functions = set()
        self.nesting_level = 0
        self.scope=[]
    
    def get_scope(self,append=None):
        """Gets the current scope for the given object.
        
        Args:
            self: The object for which to get the scope.
            append: An optional string representing a new scope element to add to the
                    current scope. If None, the current scope is returned as a string.
        
        Returns:
            A string representing the current scope for the given object. If append is
            provided, the new scope is returned as a string with the new element
            appended.
        
        Raises:
            None
        
        Notes:
            The scope is represented as a list of strings, where each string is the
            name of a containing namespace. The first element is always the global
            namespace.
        """
        if append:
            scope=self.scope.copy()
            scope.append(append)
            return ".".join(scope)
        
        
        return ".".join(self.scope)

    def visit_Module(self, node):
        """Visits a given ast.Module node and recursively visits its body elements.
        
        Args:
            node (ast.Module): The ast.Module node to visit.
        
        Returns:
            None.
        
        Raises:
            None.
        
        Notes:
            This function is a part of the AstVisitor class and is responsible for visiting
            ast.Module nodes. It iterates through the body of the node and visits each
            ast.ClassDef or ast.FunctionDef element. For other types of elements, it calls
            the visit method of the AstVisitor instance.
        """
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self.visit_ClassDef(item)  
            elif isinstance(item, ast.FunctionDef):
                self.visit_FunctionDef(item)
            else:
                self.visit(item)

    def get_obj(self,scope):
        """Gets the multi-dimentional object based on dot style location in scope.
        Args:
            self: An instance of the class.
            scope: A string representing the scope of the object to get. The string should be in the format "var.var.var..." or "func.func.func..." or "class.class.class...".
        
        Returns:
            The object that matches the given scope.
        
        Raises:
            KeyError: If the given scope cannot be found in the data dictionary of the instance.
            ValueError: If the given scope is an empty string or has no parts.
        
        Notes:
            This function searches for the given scope in the data dictionary of the instance. It uses the given scope string to traverse the dictionary by splitting it into parts and checking if each part is a key in the current object. If a part is found, the function moves to the next part until the final object is reached. If a part is not found, an error is raised.
        """
        cur_obj=self.data['root']
        if len(scope)>0 and scope !="":
            path=scope.split(".")
        
            for part in path:
                    if 'vars' in cur_obj and part in cur_obj['vars']:
                        cur_obj=cur_obj['vars'][part]
                    elif 'ret' in cur_obj and part in cur_obj['ret']:
                        cur_obj=cur_obj['ret'][part]
                    elif 'args' in cur_obj and part in cur_obj['args']:
                        cur_obj=cur_obj['args'][part]
                    elif 'func' in cur_obj and part in cur_obj['func']:
                        cur_obj=cur_obj['func'][part]
                    elif 'class' in cur_obj and part in cur_obj['class']:
                        cur_obj=cur_obj['class'][part]
                    else:
                        print(self.data)
                        print (f"Cant find {part}")
                        exit()

        return cur_obj

    def add_class(self,scope,name):
        """Adds a new class to an object in the given scope.
        
        Args:
            scope (str): The name of the scope to search for the object.
            name (str): The name of the new class to be added.
        
        Returns:
            None. The function modifies the object in the given scope.
        
        Raises:
            KeyError: If the scope does not exist.
            TypeError: If the scope is not a dictionary.
        
        Notes:
            The function assumes that the object in the given scope is a dictionary.
            If the class with the given name already exists, it is not overwritten.
        """
        obj=self.get_obj(scope)
        if 'class' not in obj:
            obj['class']={}

        obj['class'][name]={'name':name,
                    'type':'class'}
    
    def add_func(self,scope,name,start,end,column):
        """Adds a function definition to a given scope in a symbol table.
        
        Args:
            scope (str): The name of the scope in which to add the function.
            name (str): The name of the function to add.
            start (int): The line number at which the function starts.
            end (int): The line number at which the function ends.
            column (int): The column number at which the function starts.
        
        Returns:
            None. The function simply modifies the given symbol table.
        
        Raises:
            KeyError: If the given scope is not present in the symbol table.
        
        Notes:
            If the given scope is not present in the symbol table, an error is raised.
            If the function with the given name already exists in the scope, it is overwritten.
        """
        obj=self.get_obj(scope)
        if 'func' not in obj:
            obj['func']={}

        obj['func'][name]={'name':name,'start':start,'end':end,'col':column}

    def add_var(self,scope,name):
        """Adds a variable to the given scope's dictionary.
        
        Args:
            scope (str): The name of the scope (e.g. 'global' or 'local').
            name (str): The name of the variable to add.
        
        Returns:
            None.
        
        Raises:
            KeyError: If the given scope is not found.
        
        Notes:
            If the scope's dictionary does not already contain a 'vars' key, one will be created and the variable will be added to it.
        """
        obj=self.get_obj(scope)
        if 'vars' not in obj:
            obj['vars']={}

        obj['vars'][name]={'name':name}


    def add_ret(self,scope,value):
        """Adds a value to a list of returns for a given scope.
        
        Args:
            scope (str): The name of the scope to add the return to.
            value (any): The value to be added to the list of returns.
        
        Returns:
            None. This function modifies the existing dictionary for the given scope.
        
        Raises:
            KeyError: If the given scope does not exist.
        
        Notes:
            This function assumes that the dictionary for the given scope has a key named 'ret' which is a list.
            If the key 'ret' does not exist, it will be created with an empty list.
        """
        obj=self.get_obj(scope)
        if 'ret' not in obj:
            obj['ret']=[]

        obj['ret'].append(value)

    def add_arg(self,scope,arg,default,has_default=False):
        """Adds an argument to an object's list of arguments.
        
        Args:
            scope (str): The name of the scope (context) in which the argument is defined.
            arg (str): The name of the argument.
            default (Any): The default value for the argument, if it has one. This is an optional argument.
            has_default (bool, optional): A boolean indicating whether the argument has a default value. Default is False.
        
        Returns:
            None. This function modifies the given object in place.
        
        Raises:
            KeyError: If the given scope is not found in the object.
        
        Notes:
            This function modifies the given object directly, so it should be used with caution.
        """
        obj=self.get_obj(scope)
        item={'name':arg,'has_default':has_default,'scope':scope}
        if has_default==True:
            item['default']=default
        if 'args' not in obj:
            obj['args']={}

        obj['args'][arg]=item

    def visit_ClassDef(self, node):
        """Visits a ClassDef node in the Abstract Syntax Tree (AST).
        
        Args:
            node (ast.ClassDef): The node to visit.
        
        Returns:
            None
        
        Raises:
            None
        
        Notes:
            This function is called when visiting a ClassDef node in the Abstract Syntax Tree (AST).
            It sets up the necessary data structures for the class, such as the scope and nesting level.
            It also adds the class to the symbol table and calls the generic visit method to process the class body.
            Finally, it cleans up the scope and nesting level.
        """
        class_name = node.name
        scope=self.get_scope()
        self.nesting_level += 1
        self.add_class(scope,class_name)
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()
        self.nesting_level -= 1

    def visit_FunctionDef(self, node):
        """Visits a FunctionDef node in the abstract syntax tree.
        
        Args:
            node (ast.FunctionDef): The node to visit.
        
        Returns:
            None.
        
        Raises:
            None.
        
        Notes:
            This function is responsible for adding function definitions to the symbol table.
            It also handles adding arguments to the symbol table.
        
            The function takes a FunctionDef node as an argument. The node contains information about the name,
            arguments, and body of the function.
        
            The function first adds the function to the symbol table with its scope, name, start and end line numbers,
            and column offset. It then handles adding the function's arguments to the symbol table.
        
            The function uses helper methods get_scope(), add_func(), add_arg(), and defined_functions to perform these tasks.
        
            The function also handles nested functions by adding their scopes to the defined_functions list and updating the nesting level.
        """
        function_name = node.name
        scope=self.get_scope()
        self.scope.append(node.name)

        inner_scope=self.get_scope()
        self.add_func(scope,function_name,node.lineno-1,node.end_lineno+1,node.col_offset)
        defaults={}
        for arg in node.args.defaults:
            if isinstance(arg, ast.Constant):
                arg_name = node.args.args[len(node.args.defaults) - 1 - node.args.defaults.index(arg)].arg
                defaults[arg_name] = arg.value                

        for arg in node.args.args:
            has_default=False
            default=None
            if arg.arg in defaults:
                has_default=True
                default=defaults[arg.arg]
            self.add_arg(self.get_scope(),arg.arg,default,has_default)

        self.defined_functions.add(inner_scope)
        self.nesting_level += 1
        self.generic_visit(node)
        inner_scope=self.get_scope()
        self.scope.pop()
        self.nesting_level -= 1
        

    def visit_Assign(self, node):
        """
        Visits an Assign node in an Abstract Syntax Tree (AST). Assigns variables based on targets in the node.
        
        Args:
            self (ASTVisitor): The instance of the ASTVisitor class.
            node (ast.Assign): The node to visit.
        
        Returns:
            None.
        
        Raises:
            None.
        
        Notes:
            This function visits an Assign node in an Abstract Syntax Tree (AST) and assigns variables based on the targets in the node.
            If a target is an attribute, the variable name is in the format "variable_name.attribute_name".
            If a target is a Name, the variable name is simply "variable_name".
        """
        try:
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    variable_name = target.value.id+"."+target.attr
                    self.add_var(self.get_scope(),variable_name)

                if isinstance(target, ast.Name):
                    variable_name = target.id
                    self.add_var(self.get_scope(),variable_name)

        except:
            pass        
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_Return(self, node):
        """Visits a return statement node in the abstract syntax tree.
        
        Args:
            node: ast.Return: The node representing the return statement.
        
        Returns:
            None. This method updates the symbol table and the return type.
        
        Raises:
            None.
        
        Notes:
            This method gets the type of the return value and adds it to the current scope.
        """
        val=self.get_type(node.value)
        self.add_ret(self.get_scope(),val)

    def get_type(self, node):
        """This function determines the type of a given node in an Abstract Syntax Tree (AST).
        
        The node can be a call, name, string, number, list, dictionary, constant, boolean operation,
        binary operation, comparison, or function call.
        
        Args:
            node (ast.Node): The node to determine the type of.
        
        Returns:
            A dictionary with the keys 'type' and 'value' if the node is a variable, function, class, or dictionary key.
            A string representing the type if the node is a basic type (int, float, str, list, dict, function, class, or unknown).
        
        Raises:
            None
        
        Notes:
            - If the node is a variable, the value is the variable name.
            - If the node is a function, the value is the function name.
            - If the node is a class, the value is the class name.
            - If the node is a dictionary key, the value is the key string.
        """

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.defined_functions:
                return 'function'
            return 'method/external'

        elif isinstance(node, ast.Name):
            scope=self.get_scope()
            scope2=self.get_scope(node.id)
            cur_obj=self.get_obj(scope)

            if 'vars' in cur_obj and node.id in  cur_obj['vars']:
                return {'type':'variable','value':node.id}
            elif scope2 in self.defined_functions:
                return {'type':'function','value':node.id}
            elif scope2 in self.defined_classes:
                return {'type':'class','value':node.id}
            else:
                return {'type':'UNK','value':node.id}
        elif isinstance(node, ast.Str):
            return 'str'
        elif isinstance(node, ast.Num):
            return 'int' if isinstance(node.n, int) else 'float'
        elif isinstance(node, ast.List):
            if node.elts:
                return f'[ {self.get_type(node.elts[0])} ]'
            return 'list'
        elif isinstance(node, ast.Dict):
            return '{ ' + self.get_dict_keys(node) +" }"
        elif isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.BoolOp):
            return 'bool'
        elif isinstance(node, ast.BinOp):
            return self.get_binop_type(node)
        elif isinstance(node, ast.Compare):
            return 'bool'
        elif isinstance(node, ast.Call):
            return 'function: ' + self.get_function_call_path(node)
        elif isinstance(node, ast.Attribute):
            return 'attr:'+node.attr

        return 'unknown'

    def get_binop_type(self, node):
        """Determines the type of binary operation based on the types of its operands.
        
        Args:
            self: An instance of the Abstract Syntax Tree (AST) class.
            node: A node from the abstract syntax tree representing a binary operation.
        
        Returns:
            str: The type of the binary operation. Can be either 'int', 'float', or 'mixed'.
        
        Raises:
            None
        
        Notes:
            This function is used by the TypeChecker class to ensure type compatibility
            during type checking.
        """
        # This function deduces the type of binary operations (like arithmetic)
        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)
        if left_type == right_type:
            return left_type
        return 'mixed'
 
    def get_dict_keys(self, node):
        """Returns the keys of a dictonary.
        
        Args:
            node (ast.AST): The node from which to retrieve dictionary keys.
        
        Returns:
            str: A comma-separated string of the keys in the dictionary represented by the node.
        
        Raises:
            None
        
        Notes:
            This function retrieves the keys of a given dictionary node and returns them as a comma-separated string.
            The keys can be string literals, variable names, or constants.
        """
        # This method retrieves the keys of the dictionary
        keys = []
        for key in node.keys:
            if isinstance(key, ast.Str):
                keys.append(key.s)  # String literal key
            elif isinstance(key, ast.Name):
                keys.append(key.id)  # Variable name as key
            elif isinstance(key, ast.Constant):
                keys.append(str(key.value))  # Constant key (Python 3.8+)
            else:
                keys.append('unknown')
        return ', '.join(keys)

    def get_function_call_path(self, node):
        """Constructs the full function call path from an ast node.
        
        Args:
            node (ast.Call): The AST node representing a function call.
        
        Returns:
            str: The full function call path as a string.
        
        Raises:
            None
        
        Notes:
            If the node represents a simple function call (i.e., a function call with no dotted notation),
            the method returns the function name as the call path.
        
            If the node represents a method call or an attribute of an object/module,
            the method recursively calls itself with the value of the object/module as the argument,
            and appends the attribute/method name to the returned call path using a '.' separator.
        """
        # This method constructs the full function call path
        if isinstance(node.func, ast.Name):
            return node.func.id  # Simple function call
        elif isinstance(node.func, ast.Attribute):
            # Method call or attribute of an object/module
            return self.get_function_call_path(node.func.value) + '.' + node.func.attr
        return 'unknown'    

def read_file(file_path):
    """Reads the content of a file and returns it as a string.
    
    Args:
        file_path (str): The path to the file to be read.
    
    Returns:
        str: The content of the file as a string.
    
    Raises:
        FileNotFoundError: If the file does not exist at the provided path.
        Exception: If any other error occurs while reading the file.
    
    Notes:
        This function uses the built-in `open()` function to read the content of a file.
        It returns an error message if the file is not found or an error occurs during reading.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

def walk_data(arr, level=0,path=[],data=[],contents=None):
    """Walks through nested dictionaries and extracts function information.
    
    Args:
    arr: The root dictionary of the nested dictionaries.
    level: The current level of traversal. Default is 0.
    path: The current path to the dictionary being processed. Default is an empty list.
    data: A list to store the extracted function information. Default is an empty list.
    contents: The source code of the file. Default is None.
    
    Returns:
    data: A list containing function information extracted from the nested dictionaries.
    
    Raises:
    None.
    
    Notes:
    This function uses recursion to traverse the nested dictionaries and extract function information. It processes 'class' and 'func' keys in each dictionary.
    """
    #print(f"Level {level} - Size: {len(arr)}")
    if 'class' in arr and isinstance(arr['class'],dict)==True:
        for sub_arr in arr['class']:
            #print(level*' '+'Class: '+sub_arr) 
            if isinstance(arr['class'][sub_arr],dict):
                walk_data(arr['class'][sub_arr], level + 1,path+[sub_arr],data,contents)
                #data.append(res)


    if 'func' in arr and isinstance(arr['func'],dict)==True:
        for sub_arr in arr['func']:
            #print(level*' '+'func: '+sub_arr) 
            start=arr['func'][sub_arr]['start']
            end=arr['func'][sub_arr]['end']
            item={'start_line':start,
             'end_line':end,
             'name':".".join(path+[sub_arr]),
             'code':"\n".join(contents[start:end]),
             'col':arr['func'][sub_arr]['col']
             
             }
            data.append(item)
            if isinstance(arr['func'][sub_arr],dict):
                res=walk_data(arr['func'][sub_arr], level + 1,path+[sub_arr],data,contents)
                #data.append(res)
    pprint(data)
    return data


def parse(file_path):
    """Parses a Python file and returns a list of dictionaries containing information about each function and class in the file.
    
    Args:
        file_path (str): The path to the Python file to be parsed.
    
    Returns:
        list: A list of dictionaries, where each dictionary contains information about a function or class in the file.
    
    Raises:
        FileNotFoundError: If the specified file does not exist.
        SyntaxError: If there is a syntax error in the file.
        TypeError: If the file path is not a string.
    
    Notes:
        The 'contents' and 'data' variables are used internally and are not part of the public API.
    """
    contents=read_file(file_path)
    parsed_ast = ast.parse(contents)
    analyzer = FunctionAnalyzer()
    analyzer.visit(parsed_ast)
    
    data=walk_data(analyzer.data['root'],contents=contents.split("\n"),data=[])

    return data
    #return [{'name':'x=1'}]



#pprint.pprint(analyzer.returns)
#pprint.pprint(analyzer.variables)
#pprint.pprint(analyzer.returns)
#pprint.pprint(analyzer.defined_classes)
#pprint.pprint(analyzer.defined_functions)
#pprint.pprint(analyzer.data)
