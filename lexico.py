import re

def remover_comentarios(source_code):
    pattern = r'\/\*[\s\S]*?\*\/|\/\/.*'
    return re.sub(pattern, '', source_code)

def analizar(source_code):
    keyword = r"^var$|^if$|^else$|^while$|^return$|^struct$|^for$|^switch$|^case$|^break$|^default$|^print$|^true$|^false$|^and$|^or$|^fun$|ˆnil$"
    operator = r"->|=|\+\+|--|[-+*/%&<>!]=?|[-+*/%&<>]|<<|>>|\|\|"
    delimitator = r"[(),:;{}\[\]]"
    int_const = r"\d+(?="+operator+"|"+delimitator+"|\s|$)"
    identifier = r"(?<!\d)[a-zA-Z_][a-zA-Z0-9_]*(?="+operator+"|"+delimitator+"|\s|$)"
    float_const = r"\d+\.\d+(?="+operator+"|"+delimitator+"|\s|$)"
    string_const = r'\".*?\"(?='+operator+'|'+delimitator+'|\s|$)'
    char_const = r'\'.*?\'(?='+operator+'|'+delimitator+'|\s|$)'
    
    std_reco = "|".join([
        keyword, 
        identifier,
        float_const,
        int_const,
        string_const,
        char_const,
        operator, 
        delimitator
    ])
    
    invalidate = source_code
    tokens = []
    for linha in source_code.split("\n"):
        for token in re.findall(std_reco, linha):
            invalidate = invalidate.replace(token, "", 1)
            if re.match(keyword, token):
                tokens.append(('KEYWORD', token))
                continue
            elif re.match(float_const, token) or re.match(int_const, token) or re.match(int_const, token) or re.match(string_const, token) or re.match(char_const, token):
                tokens.append(('CONST', token))
                continue
            elif re.match(identifier, token):
                tokens.append(('ID', token))
                continue
            elif re.match(operator, token):
                tokens.append(('OP', token))
            elif re.match(delimitator, token):
                tokens.append(('DEL', token))

    invalidate = ''.join(invalidate.split())
    if (len(invalidate) > 0):
        print("Erro léxico, caracteres inesperados:")
        print(invalidate)
        return ''
    return tokens

def LexicalAnalyzer(source_code):
    source_code = remover_comentarios(source_code)
    tokens = analizar(source_code)
    return tokens