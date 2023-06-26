class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def parse(self):
        return self.program()

    def program(self):
        declarations = []
        while self.current_token[0] != 'EOF':
            declarations.append(self.declaration())
        return ('program', declarations)

    def declaration(self):
        if self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'var':
            return self.var_decl()
        elif self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'fun':
            return self.fun_decl()
        else:
            return self.statement()

    def if_stmt(self):
        chain = []
        self.match(('KEYWORD', 'if'))
        self.match(('DEL', '('))
        expression = self.expression()
        self.match(('DEL', ')'))
        block = self.block()

        chain.append(('ifStmt', expression, block))
        while self.current_token == ('KEYWORD', 'else'):
            self.match(('KEYWORD', 'else'))
            if self.current_token == ('KEYWORD', 'if'):
                self.match(('KEYWORD', 'if'))
                self.match(('DEL', '('))
                expression = self.expression()
                self.match(('DEL', ')'))
                block = self.block()
                chain.append(('ifStmt', expression, block))
            else:
                chain.append(('else', self.block()))
        return chain

    def var_decl(self):
        self.match(('KEYWORD', 'var'))
        variable_name = self.match(('ID', None))
        value = ""
        try:
            self.match(('OP', '='))
            value = self.expression()
        except Exception as e:
            if "Syntax Error: Expected ('OP', '='), but got ('DEL', ';')" in str(e):
                self.goBack()
            else:
                raise Exception("Syntax Error: Expected ('DEL', ';')")
        #value = self.expression()
        self.match(('DEL', ';'))
        return ('varDecl', variable_name, value)

    def fun_decl(self):
        self.match(('KEYWORD', 'fun'))
        function_name = self.match(('ID', None))
        self.match(('DEL', '('))
        parameters = []
        while self.current_token[0] != 'DEL' or self.current_token[1] != ')':
            parameters.append(self.match(('ID', None)))
            if self.current_token[0] == 'DEL' and self.current_token[1] == ',':
                self.match(('DEL', ','))
        self.match(('DEL', ')'))
        block = self.block()
        return ('funDecl', function_name, parameters, block)

    def statement(self):
        if self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'print':
            return self.print_stmt()
        elif self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'return':
            return self.return_stmt()
        elif self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'while':
            return self.while_stmt()
        elif self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'if':
            return self.if_stmt()
        else:
            return self.expression_stmt()

    def expression_stmt(self):
        expression = self.expression()
        self.match(('DEL', ';'))
        return ('expressionStmt', expression)

    def print_stmt(self):
        self.match(('KEYWORD', 'print'))
        expression = self.expression()
        self.match(('DEL', ';'))
        return ('printStmt', expression)

    def return_stmt(self):
        self.match(('KEYWORD', 'return'))
        if self.current_token[0] == 'DEL' and self.current_token[1] == ';':
            expression = None
        else:
            expression = self.expression()
        self.match(('DEL', ';'))
        return ('returnStmt', expression)

    def while_stmt(self):
        self.match(('KEYWORD', 'while'))
        self.match(('DEL', '('))
        condition = self.expression()
        self.match(('DEL', ')'))
        statement = self.statement()
        return ('whileStmt', condition, statement)

    def block(self):
        self.match(('DEL', '{'))
        declarations = []
        while self.current_token[0] != 'DEL' or self.current_token[1] != '}':
            declarations.append(self.declaration())
        self.match(('DEL', '}'))
        return ('block', declarations)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expression = self.logic_or()
        if self.current_token[0] == 'OP' and self.current_token[1] == '=':
            operator = self.match(('OP', '='))
            assignment = self.assignment()
            return ('assignment', expression, assignment)
        else:
            return expression

    def logic_or(self):
        expression = self.logic_and()
        while self.current_token[0] == 'OP' and self.current_token[1] == 'or':
            operator = self.match(('OP', 'or'))
            expression2 = self.logic_and()
            expression = ('logicOr', operator, expression, expression2)
        return expression

    def logic_and(self):
        expression = self.logic_not()
        while self.current_token[0] == 'OP' and self.current_token[1] == 'and':
            operator = self.match(('OP', 'and'))
            expression2 = self.logic_not()
            expression = ('logicAnd', operator, expression, expression2)
        return expression
    
    def logic_not(self):
        expression = self.equality()
        while self.current_token[0] == 'OP' and self.current_token[1] == '!':
            operator = self.match(('OP', '!'))
            expression2 = self.equality()
            expression = ('logicNot', operator, expression, expression2)
        return expression
    
    def equality(self):
        expression = self.comparison()
        while self.current_token[0] == 'OP' and (self.current_token[1] == '==' or self.current_token[1] == '!='):
            operator = self.match(('OP', None))
            expression2 = self.comparison()
            expression = ('equality', operator, expression, expression2)
        return expression

    def comparison(self):
        expression = self.addition()
        while self.current_token[0] == 'OP' and (self.current_token[1] == '<' or self.current_token[1] == '>' or
                                                self.current_token[1] == '<=' or self.current_token[1] == '>='):
            operator = self.match(('OP', None))
            expression2 = self.addition()
            self.advance()
            logic = self.logic_or()
            if logic == None:
                self.goBack()
            expression = ('comparison', operator, expression, expression2)
        return expression

    def addition(self):
        expression = self.multiplication()
        while self.current_token[0] == 'OP' and (self.current_token[1] == '+' or self.current_token[1] == '-'):
            operator = self.match(('OP', None))
            expression2 = self.multiplication()
            expression = ('addition', operator, expression, expression2)
        return expression

    def multiplication(self):
        expression = self.unary()
        while self.current_token[0] == 'OP' and (self.current_token[1] == '*' or self.current_token[1] == '/'):
            operator = self.match(('OP', None))
            expression2 = self.unary()
            expression = ('multiplication', operator, expression, expression2)
        return expression

    def unary(self):
        if self.current_token[0] == 'OP' and (self.current_token[1] == '-' or self.current_token[1] == 'not'):
            operator = self.match(('OP', None))
            expression = self.unary()
            return ('unary', operator, expression)
        else:
            return self.call()

    def call(self):
        expression = self.primary()
        while self.current_token[0] == 'DEL' and self.current_token[1] == '(':
            arguments = self.argument_list()
            expression = ('call', expression, arguments)
        return expression

    def argument_list(self):
        self.match(('DEL', '('))
        arguments = []
        while self.current_token[0] != 'DEL' or self.current_token[1] != ')':
            arguments.append(self.expression())
            if self.current_token[0] == 'DEL' and self.current_token[1] == ',':
                self.match(('DEL', ','))
        self.match(('DEL', ')'))
        return arguments

    def primary(self):
        if self.current_token[0] == 'ID':
            identifier = self.match(('ID', None))
            return ('identifier', identifier)
        elif self.current_token[0] == 'CONST':
            value = self.match(('CONST', None))
            return ('const', value)
        elif self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'true' or 'KEYWORD' and self.current_token[1] == 'false':
            value = self.match(('KEYWORD', None))
            return ('const',  value)
        elif self.current_token[0] == 'DEL' and self.current_token[1] == '(':
            self.match(('DEL', '('))
            expression = self.expression()
            self.match(('DEL', ')'))
            return expression

    def match(self, expected_token):
        if (self.current_token == ('EOF', None) and expected_token != ('EOF', None)):
            raise Exception(f"Syntax Error: Expected {expected_token[0]}, but got end of file")
        
        if self.current_token == expected_token or expected_token[1] in (None, ';'):
            token = self.current_token
            self.advance()
            return token
        else:
            raise Exception(f"Syntax Error: Expected {expected_token}, but got {self.current_token}")

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = ('EOF', None)

    def goBack(self):
        self.current_token_index -= 1
        if self.current_token_index > 0:
            self.current_token = self.tokens[self.current_token_index]
        else:
            return None