
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
        # param: -? (NUMBER | variable)
        # CONTINUE: 
        value = ''
        if self.current_token.tokenType == TokenType.MINUS:
            value += '-'
            self.eat(TokenType.MINUS)
        if self.current_token.tokenType == TokenType.NUMBER:
            value += self.current_token.value
            self.eat(TokenType.NUMBER)
            return value
        value = self.expr()
        return value

    def function_params(self):
        # function_params: LPAREN param (COMMA param)* RPAREN
        self.eat(TokenType.LPAREN)
        params = []
        params.append(self.param())
        while self.current_token.value == ',':
            self.eat(TokenType.COMMA)
            params.append(self.param())
        self.eat(TokenType.RPAREN)
        return '(' + ','.join(params) + ')'

    def expr(self):
        # expr: function | variable
        v = self.current_token.value
        self.eat(TokenType.ID)

        if self.current_token.value == '.':
            v += self.current_token.value
            self.eat(TokenType.DOT)
            v += self.current_token.value
            self.eat(TokenType.ID)
        elif self.current_token.value == '(':
            # function
            v = v + self.function_params()
        return v

    def mul(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return (f'{dest} = {arg1} * {arg2};')

    def add(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        self.eat(TokenType.COMMA)
        arg2 = self.expr()
        return (f'{dest} = {arg1} + {arg2};')

    def exp(self):
        dest = self.expr()
        self.eat(TokenType.COMMA)
        arg1 = self.expr()
        return (f'{dest} = exp2({arg1});')

    # def log(self):  pass

    # def mad(self):  pass
    # def sqrt(self):  pass
    # def div(self):  pass

    # def dp4(self):  pass
    # def dp2(self):  pass
    # def dp3(self):  pass

    # def ret(self):  pass

    # def min(self):  pass
    # def max(self):  pass
    # def max(self):  pass


    def instruction(self):
        method_name = self.current_token.value
        self.eat(TokenType.ID)
        func = getattr(self, method_name, None)
        if not func:
            return (f'No Implementation For [{method_name}]')
        return func()
        # func = getattr(self, method_name, None)
        # return func()
            
    def parse(self):
        return self.instruction()
        # while self.current_token:
            # print(self.current_token)
            # self.current_token = self.lexer.get_next_token()


with open('test.txt', 'r') as in_file:
    for line in in_file:
        line = line.partition(':')[2].replace('\n', '')
        parser = Parser(Tokenizer(line))
        result = parser.parse()
        print(result)


#    0: sample_indexable(texture2d)(float,float,float,float) r0.xyzw, v4.xyxx, diffuseTex.xyzw, g_linear  
#    1: mul				r0.w, r0.w, v5.w  
#    2: mul				r0.w, r0.w, me_colour.w   
#    3: mad				r1.xy, v4.xyxx, l(2.0000, 2.0000, 0.0000, 0.0000), l(-1.0000, -1.0000, 0.0000, 0.0000)    