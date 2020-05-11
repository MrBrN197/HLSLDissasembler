
from enum import Enum


class TokenType(Enum):
    ID = 'ID'
    LPAREN = '('
    RPAREN = ')'
    COMMA = ','
    DOT = '.'


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
        self.current_char = self.text[self.pos]

    def advance(self):
        if self.pos < len(self.text) - 1:
            self.pos += 1
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def _id(self):
        text = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            text += self.current_char
            self.advance()
        return text

    def skip_whitespace(self):
        while self.current_char and self.current_char == ' ':
            self.advance()

    def get_next_token(self):
        while self.current_char:
            if self.current_char == ' ':
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                return Token(TokenType('ID'), self._id())
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

    def mul(self):
        pass

    def instruction(self):
        method_name = self.current_token.value
        print(method_name)
        # func = getattr(self, method_name, None)
        # return func()
            
    def parse(self):
        self.instruction()
        # while self.current_token:
            # print(self.current_token)
            # self.current_token = self.lexer.get_next_token()


with open('test.txt', 'r') as in_file:
    for line in in_file:
        line = line.partition(':')[2].replace('\n', '')
        parser = Parser(Tokenizer(line))
        parser.parse()
