import pprint
import ast

        
        

class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.data={'root':{}}
        self.defined_classes = set()
        self.defined_functions = set()
        self.nesting_level = 0
        self.scope=[]
        self.variables={}
        self.returns={}
        self.attribs={}
    
    def get_scope(self,append=None):
        if append:
            scope=self.scope.copy()
            scope.append(append)
            return ".".join(scope)
        
        
        return ".".join(self.scope)

    def visit_Module(self, node):
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self.visit_ClassDef(item)  
            elif isinstance(item, ast.FunctionDef):
                self.visit_FunctionDef(item)
            else:
                self.visit(item)

    def get_obj(self,scope):
        print(f"Scope:{scope}")
        cur_obj=self.data['root']
        if len(scope)>0 and scope is not "":
            path=scope.split(".")
        
            for part in path:
                    #print(part)
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
        print(f"Add Class: {name}, Scope {scope}")
        #self.curent_object['func'].append()
        obj=self.get_obj(scope)
        if 'class' not in obj:
            obj['class']={}

        obj['class'][name]={'name':name,
                    'type':'class'}
    
        


    def add_func(self,scope,name):
        print(f"Add Func: {name}, Scope {scope}")
        #self.curent_object['func'].append()
        obj=self.get_obj(scope)
        if 'func' not in obj:
            obj['func']={}

        obj['func'][name]={'name':name}

    def add_var(self,scope,name):
        obj=self.get_obj(scope)
        if 'vars' not in obj:
            obj['vars']={}

        obj['vars'][name]={'name':name}
        #self.data[scope]['vars'].append({'name':name})


    def add_ret(self,scope,value):
        obj=self.get_obj(scope)
        if 'ret' not in obj:
            obj['ret']=[]

        obj['ret'].append(value)
        #self.data[scope]['vars'].append({'name':name})


        #self.data[name]['ret'].append({'value':value})

    def add_arg(self,scope,arg,default,has_default=False):
        obj=self.get_obj(scope)
        print(obj)
        item={'name':arg,'has_default':has_default,'scope':scope}
        if has_default==True:
            item['default']=default
        if 'args' not in obj:
            obj['args']={}

        obj['args'][arg]=item

    def visit_ClassDef(self, node):
        class_name = node.name
        scope=self.get_scope()
        print(f"{'  ' * self.nesting_level} C: {class_name}")
        self.nesting_level += 1
        self.add_class(scope,class_name)

        self.scope.append(node.name)
        self.generic_visit(node)

        
        inner_scope=self.get_scope()

        #self.defined_classes.add(inner_scope)
        
        for key in self.variables:
            if key==inner_scope:
                for var in self.variables[key]:
                    print(f"{'  ' * self.nesting_level}V: {var} ")

        self.scope.pop()
        self.nesting_level -= 1

    def visit_FunctionDef(self, node):
        function_name = node.name
        scope=self.get_scope()

        arguments = [arg.arg for arg in node.args.args]


        print(f"{'  ' * self.nesting_level}F: {function_name} ( {', '.join(arguments)} )")
        self.scope.append(node.name)

        inner_scope=self.get_scope()
        self.add_func(scope,function_name)
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
        
        for key in self.variables:
            if key==inner_scope:
                for var in self.variables[key]:
                    print(f"{'  ' * self.nesting_level}V: {var} ")

        #for key in self.attribs:
        #    if key==inner_scope:
        #        for var in self.attribs[key]:
        #            print(f"{'  ' * self.nesting_level}A: {var} ")

        return_types=""
        
        if inner_scope in self.returns:
            returns=[]
            for item in self.returns[inner_scope]:
                if isinstance(item,str)==True:
                    returns.append(item)
                elif isinstance(item,dict)==True:
                    print(item)
                    returns.append(f"{item['type']}:{item['value']}")
                else:
                    print(list)
                    exit()
            return_types="< "+" | ".join(returns)+" >"

        else:
            return_types=None
        print(f"{'  ' * self.nesting_level}R: {return_types}")

        self.scope.pop()
        self.nesting_level -= 1
        

    def visit_Assign(self, node):
        scope=self.get_scope()
        if scope not in self.variables:
            self.variables[scope]=[]

        variables={}
        # Assignment statement
        try:
            for target in node.targets:
                #pprint.pprint(target)
                if isinstance(target, ast.Attribute):
                    variable_name = target.value.id+"."+target.attr
                    if variable_name not in self.variables[scope]:
                        self.variables[scope].append(variable_name)
                        self.add_var(self.get_scope(),variable_name)

                if isinstance(target, ast.Name):
                    variable_name = target.id
                    if variable_name not in self.variables[scope]:
                        self.variables[scope].append(variable_name)
                        self.add_var(self.get_scope(),variable_name)

        except:
            pass        
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
       # pprint.pprint(self.attribs)

    def visist_Attribute(self, node):
        return
        scope=self.get_scope()
        if scope not in self.attribs:
            self.attribs[scope]=[]

        val=self.get_type(node)
        if val not in self.attribs[scope]:
            self.attribs[scope].append(val)

    def visit_Return(self, node):
        scope=self.get_scope()
        if scope not in self.returns:
            self.returns[scope]=[]

        val=self.get_type(node.value)
        if val not in self.returns[scope]:
            self.returns[scope].append(val)
            self.add_ret(self.get_scope(),val)

    def get_type(self, node):

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.defined_functions:
                return 'function'
            return 'method/external'

        elif isinstance(node, ast.Name):
            scope=self.get_scope()
            scope2=self.get_scope(node.id)
            if scope in self.variables and node.id in self.variables[scope]:
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
            return None

        
        #print(node)
        # Extend with other types as needed
        return 'unknown'

    def get_binop_type(self, node):
        # This function deduces the type of binary operations (like arithmetic)
        left_type = self.get_type(node.left)
        right_type = self.get_type(node.right)
        if left_type == right_type:
            return left_type
        return 'mixed'
 
    def get_dict_keys(self, node):
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
        # This method constructs the full function call path
        if isinstance(node.func, ast.Name):
            return node.func.id  # Simple function call
        elif isinstance(node.func, ast.Attribute):
            # Method call or attribute of an object/module
            return self.get_function_call_path(node.func.value) + '.' + node.func.attr
        return 'unknown'    

# Example usage

def read_file(file_path):#3
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

parsed_ast = ast.parse(read_file('/home/nd/repos/Projects/ddb/ddb/source/ddb/methods/record_select.py'))
analyzer = FunctionAnalyzer()
analyzer.visit(parsed_ast)


#pprint.pprint(analyzer.returns)
#pprint.pprint(analyzer.variables)
#pprint.pprint(analyzer.returns)
#pprint.pprint(analyzer.defined_classes)
#pprint.pprint(analyzer.defined_functions)
pprint.pprint(analyzer.data)
