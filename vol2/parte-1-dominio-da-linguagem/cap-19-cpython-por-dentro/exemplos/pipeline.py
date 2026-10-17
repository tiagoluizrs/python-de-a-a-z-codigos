"""Do texto ao resultado: tokens, AST, escopos, bytecode, execução."""
import ast
import dis
import io
import tokenize
import symtable

source = "total = price * 2 + 1\n"

# 1) Análise léxica: texto -> tokens
tokens = [(tokenize.tok_name[t.type], t.string) for t in tokenize.generate_tokens(io.StringIO(source).readline)]
print(tokens)

# 2) Análise sintática: tokens -> árvore (AST)
tree = ast.parse(source)
print(ast.dump(tree.body[0]))

# 3) Tabela de símbolos: quem é local, global, livre
code_text = "def f(a):\n    b = a\n    return b + g\n"
table = symtable.symtable(code_text, "<demo>", "exec")
f_table = table.lookup("f").get_namespace()
print([(s.get_name(), "param" if s.is_parameter() else "local" if s.is_local() else "global" if s.is_global() else "?")
       for s in f_table.get_symbols()])

# 4) Geração de bytecode: árvore -> objeto de código
code = compile(tree, "<demo>", "exec")
print(type(code).__name__, code.co_names, code.co_consts)
dis.dis(code)

# 5) Execução: a máquina virtual interpreta o bytecode
namespace = {"price": 10}
exec(code, namespace)
print(namespace["total"])

# O mesmo, de uma vez: compile aceita texto ou AST
print(eval(compile("2 ** 10", "<e>", "eval")))
