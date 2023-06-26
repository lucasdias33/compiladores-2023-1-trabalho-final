def translate_to_python(tree, indentation_level=0):
    node_type = tree[0]
    indent = '    ' * indentation_level
    old_tree = tree
    if type(node_type) == tuple:
        node_type = node_type[0]
        tree = tree[0]
    if node_type == 'program':
        statements = [translate_to_python(stmt, indentation_level) for stmt in tree[1]]
        return '\n'.join(statements)
    
    elif node_type == 'ifStmt':
        condition = translate_to_python(tree[1], indentation_level)
        block = translate_to_python(tree[2], indentation_level + 1)
        result = f'{indent}if {condition}:\n{block}'
        for elif_block in old_tree[1:]:
            if (elif_block[0] != 'else'):
                condition = translate_to_python(elif_block[1], indentation_level)
                block = translate_to_python(elif_block[2], indentation_level + 1)
                result += f'\n{indent}elif {condition}:\n{block}'
            else:
                condition = ""
                block = translate_to_python(elif_block[1], indentation_level + 1)
                result += f'\n{indent}else:\n{block}'
        return result

    elif node_type == 'else':
        block = translate_to_python(tree[1], indentation_level + 1)
        return f'{indent}else:\n{block}'

    elif node_type == 'varDecl':
        variable_name = tree[1][1]
        value = translate_to_python(tree[2], indentation_level)
        if value == 'nil':
            value = 'None'
        return f'{indent}{variable_name} = {value}'

    elif node_type == 'funDecl':
        function_name = tree[1][1]
        parameters = ', '.join([param[1] for param in tree[2]])
        block = translate_to_python(tree[3], indentation_level + 1)
        return f'def {function_name}({parameters}):\n{block}'
    
    elif node_type == 'printStmt':
        expression = translate_to_python(tree[1], indentation_level)
        return f'{indent}print({expression})'

    elif node_type == 'returnStmt':
        if tree[1] is None:
            return f'{indent}return'
        else:
            expression = translate_to_python(tree[1], indentation_level)
            return f'{indent}return {expression}'

    elif node_type == 'block':
        statements = [translate_to_python(stmt, indentation_level) for stmt in tree[1]]
        return '\n'.join(statements)
    
    elif node_type == 'expressionStmt':
        expression = translate_to_python(tree[1], indentation_level)
        return f'{indent}{expression}'
    
    elif node_type in ('addition', 'multiplication', 'equality', 'comparison', 'logicAnd', 'LogicOr'):
        left = translate_to_python(tree[2], indentation_level)
        right = translate_to_python(tree[3], indentation_level)
        operator = tree[1][1]
        return f'{left} {operator} {right}'

    elif node_type == 'assignment':
        left = translate_to_python(tree[1], indentation_level)
        right = translate_to_python(tree[2], indentation_level)
        return f'{left} = {right}'  

    elif node_type in ('logicNot', 'unary'):
        expression = translate_to_python(tree[2], indentation_level)
        operator = tree[1][1]
        return f'{operator} {expression}'

    elif node_type == 'call':
        function_name = translate_to_python(tree[1], indentation_level)
        arguments = ', '.join([translate_to_python(arg, indentation_level) for arg in tree[2]])
        return f'{function_name}({arguments})'

    elif node_type in ('identifier', 'const'):
        return tree[1][1]

    else:
        return ''