# Parser : By Rahul Manghwani  and Xiang Zhang @ New York University

"""

<sexp>    	:: <string> | <list>
<string>   	:: <display>? <simple-string> ;
<simple-string>	:: <raw> | <token> | <base-64> | <hexadecimal> | 
		           <quoted-string> ;
<display>  	:: "[" <simple-string> "]" ;
<raw>      	:: <decimal> ":" <bytes> ;
<decimal>  	:: <decimal-digit>+ ;
		-- decimal numbers should have no unnecessary leading zeros
<bytes> 	-- any string of bytes, of the indicated length
<token>    	:: <tokenchar>+ ;
<base-64>  	:: <decimal>? "|" ( <base-64-char> | <whitespace> )* "|" ;
<hexadecimal>   :: "#" ( <hex-digit> | <white-space> )* "#" ;
<quoted-string> :: <decimal>? <quoted-string-body>  
<quoted-string-body> :: "\"" <bytes> "\""
<list>     	:: "(" ( <sexp> | <whitespace> )* ")" ;
<whitespace> 	:: <whitespace-char>* ;
<token-char>  	:: <alpha> | <decimal-digit> | <simple-punc> ;
<alpha>       	:: <upper-case> | <lower-case> | <digit> ;
<lower-case>  	:: "a" | ... | "z" ;
<upper-case>  	:: "A" | ... | "Z" ;
<decimal-digit> :: "0" | ... | "9" ;
<hex-digit>     :: <decimal-digit> | "A" | ... | "F" | "a" | ... | "f" ;
<simple-punc> 	:: "-" | "." | "/" | "_" | ":" | "*" | "+" | "=" ;
<whitespace-char> :: " " | "\t" | "\r" | "\n" ;
<base-64-char> 	:: <alpha> | <decimal-digit> | "+" | "/" | "=" ;
<null>        	:: "" ;
"""

from pyparsing import *
from base64 import b64decode
import pprint
import itertools

class Parser():

  def verifyLen(self, s,l,t):
      t = t[0]
      if t.len is not None:
        t1len = len(t[1])
        if t1len != t.len:
            raise ParseFatalException(s,l,\
                    "invalid data of length %d, expected %s" % (t1len, t.len))
      return t[1]
   
  def buildGrammar(self):
      # define punctuation literals
      LPAR, RPAR, LBRK, RBRK, LBRC, RBRC, VBAR = map(Suppress, "()[]{}|")

      decimal = Regex(r'0|[1-9]\d*').setParseAction(lambda t: int(t[0]))
      hexadecimal = ("#" + OneOrMore(Word(hexnums)) + "#")\
                .setParseAction(lambda t: int("".join(t[1:-1]),16))
      bytes = Word(printables)
      raw = Group(decimal("len") + Suppress(":") + bytes).setParseAction(self.verifyLen)
      token = Word(alphanums + "-./_:*+=")
      base64_ = Group(Optional(decimal|hexadecimal,default=None)("len") + VBAR 
          + OneOrMore(Word( alphanums +"+/=" )).setParseAction(lambda t: b64decode("".join(t)))
          + VBAR).setParseAction(self.verifyLen)
    
      qString = Group(Optional(decimal,default=None)("len") + 
                        dblQuotedString.setParseAction(removeQuotes)).setParseAction(self.verifyLen)
      simpleString = base64_ | raw | decimal | token | hexadecimal | qString

      # extended definitions
      decimal = Regex(r'-?0|[1-9]\d*').setParseAction(lambda t: int(t[0]))
      real = Regex(r"[+-]?\d+\.\d*([eE][+-]?\d+)?").setParseAction(lambda tokens: float(tokens[0]))
      token = Word(alphanums + "-./_:*+=!<>")

      simpleString = real | base64_ | raw | decimal | token | hexadecimal | qString

      display = LBRK + simpleString + RBRK
      string_ = Optional(display) + simpleString

      sexp = Forward()
      sexpList = Group(LPAR + ZeroOrMore(sexp) + RPAR)
      sexp << ( string_ | sexpList )
      return sexp


