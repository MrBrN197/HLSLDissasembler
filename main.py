
from enum import Enum


class TokenType(Enum):
    ID = 'ID'
    NUMBER = 'NUMBER'
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    DOT = '.'
    MINUS = '-'


class Token():
    def __init__(self, tokenType: TokenType, value: str):
        self.tokenType = tokenType
        self.value = value
    
    def __str__(self):
        return f'{self.tokenType:<20} {self.value}'

    __repr__ = __str__


class Tokenizer():

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char: str = self.text[self.pos]

    def advance(self):
        if self.pos < len(self.text) - 1:
            self.pos += 1
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def get_id(self):
        text = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            text += self.current_char
            self.advance()

        return Token(TokenType('ID'), text) # return Token(TokenType('OPCODE'), text)

    def get_number(self):
        number = ''
        while self.current_char.isdigit():
            number += self.current_char
            self.advance()

        if self.current_char == '.':
            number += self.current_char
            self.advance()
            while self.current_char.isdigit():
                number += self.current_char
                self.advance()

        return Token(TokenType('NUMBER'), number)

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                return self.get_id()
            if self.current_char.isdigit():
                return self.get_number()
            try:
                token_type = TokenType(self.current_char) 
            except Exception as e:
                print(f'ERROR {e}')
                raise e
            else:
                self.advance()
                return Token(tokenType=token_type, value=token_type.value)
            assert False
        return None

class Node:
    pass


class BinOp(Node):
    def __init__(self, left: Node, right: Node, op: str):
        self.left = left
        self.op = op
        self.right = right

class Assign(Node):
    def __init__(self, dest: Node, src: Node):
        self.dest = dest
        self.src = src

class ConditionalAssign(Node):
    def __init__(self, dest: Node, condition: Node, src1: Node, src2: Node):
        self.dest = dest
        self.condition = condition
        self.src1 = src1
        self.src2 = src2

class Comparison(Node):
    def __init__(self, compareOp: str, left: Node, right: Node):
        self.compareOp = compareOp
        self.left = left
        self.right = right

class Var(Node):
    def __init__(self, varName):
        self.varName = varName

class ProcCall(Node):
    def __init__(self, procName, arguments):
        assert type(arguments) == list
        self.procName = procName
        self.arguments = arguments

class Number(Node):
    def __init__(self, number):
        self.number = number


class Negated(Node):
    def __init__(self, innerNode):
        self.innerNode = innerNode

class And():
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

class Or():
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def eat(self, token_type):
        if token_type == self.current_token.tokenType:
            self.current_token = self.lexer.get_next_token()
        else:
            assert False

    def param(self):
        # param: -?(NUMBER | expr)
        result = None
        negated = False
        if self.current_token.tokenType == TokenType.MINUS:
            negated = True
            self.eat(TokenType.MINUS)
        if self.current_token.tokenType == TokenType.NUMBER:
            value = self.current_token.value
            self.eat(TokenType.NUMBER)
            result = Number(value)
        else:
            result = self.expr()

        if negated:
            result = Negated(result)
        return result

    def function_params(self):
        # function_params: LPAREN param (COMMA param)* RPAREN
        self.eat(TokenType.LPAREN)
        params = []
        params.append(self.param())
        while self.current_token.value == ',':
            self.eat(TokenType.COMMA)
            params.append(self.param())
        self.eat(TokenType.RPAREN)
        return params
        # return '(' + ','.join(params) + ')'

    def expr(self):
        # expr: -?(function | variable)
        negated = False
        if self.current_token.value == '-':
            self.eat(TokenType.MINUS)
            negated = True
        v = self.current_token.value
        self.eat(TokenType.ID)
        result = None

        if self.current_token.value == '.':
            while self.current_token and self.current_token.value == '.':
                v += self.current_token.value
                self.eat(TokenType.DOT)
                v += self.current_token.value
                self.eat(TokenType.ID)
            result = Var(v)
        elif self.current_token.value == '(':
            # function
            params = self.function_params()
            if v == 'l':
                v = f'float{len(params)}'
            # v = v + '(' + ','.join(params) + ')'
            result = ProcCall(v, [p for p in params])

        if negated:
            result = Negated(result)
        return result

    def parse_mul(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        # return (f'{dest} = {arg1} * {arg2};')
        src = BinOp(arg1, arg2, '*')
        return Assign(dest, src)

    def parse_add(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        # return (f'{dest} = {arg1} + {arg2};')
        src = BinOp(arg1, arg2, '+')
        return Assign(dest, src)

    def parse_mad(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        self.eat(TokenType.COMMA)
        arg3 = self.expr()
        # return (f'{dest} = {arg1} + {arg2};')
        arg12 = BinOp(arg1, arg2, '*')
        src = BinOp(arg12, arg3, '+')
        return Assign(dest, src)

    def parse_div(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        src = BinOp(arg1, arg2, '/')
        return Assign(dest, src)

    def parse_exp(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        src = ProcCall('exp2', [arg1])
        return Assign(dest, src)

    def parse_log(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        src = ProcCall('log2', [arg1])
        return Assign(dest, src)

    def parse_sqrt(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        src = ProcCall('sqrt', [arg1])
        return Assign(dest, src)

    def parse_mov(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        src = self.expr()
        return Assign(dest, src)

    def parse_movc(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        cond = self.expr()
        self.eat(TokenType.COMMA)
        src1 = self.expr()
        self.eat(TokenType.COMMA)
        src2 = self.expr()
        return ConditionalAssign(dest, cond, src1, src2)

    def parse_and(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return Assign(dest, And(arg1, arg2))

    def parse_or(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return Assign(dest, Or(arg1, arg2))

    # def parse_ieq(self):
    #     dest = self.expr()
    #     self.eat(TokenType.COMMA)
    #     arg1 = self.expr()
    #     self.eat(TokenType.COMMA)
    #     arg2 = self.expr()
    #     return Assign(dest, Comparison('==', arg1, arg2))

    def parse_ge(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return Assign(dest, Comparison('>=', arg1, arg2))

    def parse_lt(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return Assign(dest, Comparison('<', arg1, arg2))

    # def dp4(self):  pass
    # def dp2(self):  pass
    # def dp3(self):  pass

    # def ret(self):  pass

    def parse_min(self):
        dst = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        src = ProcCall('min', [arg1, arg2])
        return Assign(dst, src)

    def parse_max(self):
        dst = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        src = ProcCall('max', [arg1, arg2])
        return Assign(dst, src)

    def instruction(self):
        method_name = self.current_token.value
        self.eat(TokenType.ID)
        func = getattr(self, 'parse_' + method_name, None)
        if not func:
            return [method_name, None]
        return [method_name, func()]
            
    def parse(self):
        return self.instruction()


class Translator:
    def __init__(self):
        pass

    def convert(self, root: Node):
        return self.translate(root) + ';'

    def translate(self, node: Node):
        method_name = 'translate_' + type(node).__name__
        func = getattr(self, method_name, None)
        if not func:
            raise Exception(f"No Implementation for {method_name}")
        return func(node)

    def translate_Number(self, node: Number):
        return node.number

    def translate_Negated(self, node: Negated):
        return '-' + self.translate(node.innerNode)

    def translate_Or(self, node: Or):
        return '[Or]'

    def translate_And(self, node: And):
        return '[And]'

    def translate_Comparison(self, node: Comparison):
        return '[Comparison]'

    def translate_ProcCall(self, node: ProcCall):
        args = ', '.join([self.translate(n) for n in node.arguments])
        return f'{node.procName}({args})'

    def translate_BinOp(self, node: BinOp):
        return f'{self.translate(node.left)} {node.op} {self.translate(node.right)}'

    def translate_Var(self, node: Var):
        return node.varName

    def translate_Assign(self, node: Assign):
        # TODO: get correct types
        return f'float4 {self.translate(node.dest)} = {self.translate(node.src)}'

    def translate_ConditionalAssign(self, node: ConditionalAssign):
        # TODO: get correct types
        return f'float4 {self.translate(node.dest)} = ({self.translate(node.condition)}) ? {self.translate(node.src1)} : {self.translate(node.src2)}'


with open('test.txt', 'r') as in_file:
    for line in in_file:
        line = line.partition(':')[2].replace('\n', '')
        parser = Parser(Tokenizer(line))
        opcode, result = parser.parse()
        if result:
            translator = Translator()
            code = translator.convert(result)
            print(code)
        else:
            print(f'No Implementation for {opcode}')