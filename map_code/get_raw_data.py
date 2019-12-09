import os
import time
import json
import re
from random import shuffle
exp_start = 1
exp_end = 16

def clean_code(code):
    code = code.lower()
    #delete line comment
    if '/*'in code:
        line_comment = re.compile(r'/\*((?:.|\n)*?)\*/')
        code = re.sub(line_comment,'',code)
    if '//' in code:
        line_comment = re.compile(r'//(.*?)\n')
        code = re.sub(line_comment,'',code)
    #tokenize
    code = " ".join([item for item in code.split() if "@" not in item])
    code = ' '.join(filter(None,re.split(r'(<>|\[\]|\(\)|<=|>=|\|\||&&|\*=|-=|\+=|--|\+\+|==|!=|=|!|>|<|[}{\[\]\(\)\s.,":;])', code))).split()
    code = ' '.join(code)
    return code
def clean_sbt(sbt):
    sbt = ' '.join(' '.join(filter(None, re.split(r'([\(\)])', sbt))).split())
    return sbt 
def clean_ast(ast):
    ast = ' '.join(' '.join(filter(None, re.split(r'([#])', ast))).split())
    return ast
def clean_doc(doc):
    doc = doc.lower()
    #delete tag infomation like <t>
    tag_info = re.compile(r'<(.*?)>')
    doc = re.sub(tag_info, '', doc)
    #delete illegal character
    illegal_format = re.compile(r'[^a-z.?!]')
    doc = re.sub(illegal_format, ' ', doc)
    doc = ' '.join(re.split(r'[.,?]',doc)[0].split())
    if len(doc.split()) <= 3 or len(doc)<=14:
        return ""
    return doc

cleanCode = []
cleanNl = []
cleanAST = []
cleanSBT = []
cleanPnl = []
for i in range(exp_start, exp_end+1):
    passed_info_dir = "../result_file/" + str(i) + "_exp_result/passed_dataset"
    print("dealing with the", i, "th experiment>>>>>>>>>>>>>>>>>>>>>>>")
    for root, dir, files in os.walk(passed_info_dir):
        if len(files) == 1:
            raw_data_path = os.path.join(root, files[0])
            with open(raw_data_path,"r",encoding = 'utf8') as f:
                info = json.load(f)
                info = [item for item in info if item["passed_comments"] != "/"]
                for single_method_info in info:
                    raw_doc = single_method_info["methodDoc"]
                    doc = clean_doc(raw_doc)
                    passed_docs = ""
                    for item in single_method_info["passed_comments"]:
                        for k,v in item.items():
                            if clean_doc(v) != "":
                                passed_docs += clean_doc(v) + " ## "
                    if  doc == "" or passed_docs == "":
                        continue
                    raw_code = single_method_info["methodBody"]
                    raw_sbt = single_method_info["SBT"]
                    raw_ast = single_method_info["AST"]
                    cleanCode.append(clean_code(raw_code))
                    cleanNl.append(doc)
                    cleanPnl.append(passed_docs)
                    cleanSBT.append(clean_sbt(raw_sbt))
                    cleanAST.append(clean_ast(raw_ast))

#shuffle the training data
all_data = list(zip(cleanCode, cleanNl, cleanPnl, cleanAST, cleanSBT))
shuffle(all_data)
cleanCode, cleanNl, cleanPnl, cleanAST, cleanSBT = zip(*all_data)
#all data writing
print("all item len:", len(cleanCode))
print("writing the whole data to traindata/all...")
with open("../traindata/all/train.token.code","w") as f1, \
    open("../traindata/all/train.token.nl","w") as f2, \
    open("../traindata/all/train.token.pnl","w") as f3, \
    open("../traindata/all/train.token.ast","w") as f4, \
    open("../traindata/all/train.token.sbt","w") as f5:
    for a,b,c,d,e in zip(cleanCode, cleanNl, cleanPnl, cleanAST, cleanSBT):
        f1.write(a + '\n')
        f2.write(b + '\n')
        f3.write(c + '\n')
        f4.write(d + '\n')
        f5.write(e + '\n')
#10-folds
length = int(len(cleanCode)/10)
code_folds = []
nl_folds = []
pnl_folds = []
ast_folds = []
sbt_folds = []
for i in range(9):
    code_folds += [cleanCode[i*length: (i+1)*length]]
    nl_folds += [cleanNl[i*length: (i+1)*length]]
    pnl_folds += [cleanPnl[i*length: (i+1)*length]]
    ast_folds += [cleanAST[i*length: (i+1)*length]]
    sbt_folds += [cleanSBT[i*length: (i+1)*length]]
code_folds += [cleanCode[9*length: len(cleanCode)]]
nl_folds += [cleanNl[9*length: len(cleanNl)]]
pnl_folds += [cleanPnl[9*length: len(cleanPnl)]]
ast_folds += [cleanAST[9*length: len(cleanAST)]]
sbt_folds += [cleanSBT[9*length: len(cleanSBT)]]
def get_remain_list(all, item):
    result = []
    for item in [remain for remain in all if remain != item]:
        result += item
    return result

for i in range(1,11):
    print("writing the data to traindata/"+str(i)+"-folds...")
    path = "../traindata/10-folds/" + str(i) +"_fold"
    if not os.path.exists(path):
        os.mkdir(path) 
    train_dir = os.path.join(path, "train")
    test_dir = os.path.join(path, "test" )
    if not os.path.exists(train_dir):
        os.mkdir(train_dir)
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    test_data = [code_folds[i-1], nl_folds[i-1], pnl_folds[i-1], ast_folds[i-1], sbt_folds[i-1]]
    train_data =[get_remain_list(code_folds, code_folds[i-1]),\
        get_remain_list(nl_folds, nl_folds[i-1]),\
        get_remain_list(pnl_folds, pnl_folds[i-1]),\
        get_remain_list(ast_folds, ast_folds[i-1]),\
        get_remain_list(sbt_folds, sbt_folds[i-1])]
    with open(os.path.join(train_dir,"train.token.code"), "w") as f1,\
        open(os.path.join(train_dir,"train.token.nl"), "w") as f2,\
        open(os.path.join(train_dir,"train.token.pnl"), "w") as f3,\
        open(os.path.join(train_dir,"train.token.ast"), "w") as f4,\
        open(os.path.join(train_dir,"train.token.sbt"), "w") as f5:
        for a,b,c,d,e in zip(train_data[0], train_data[1], train_data[2], train_data[3], train_data[4]):
            f1.write(a + '\n')
            f2.write(b + '\n')
            f3.write(c + '\n')
            f4.write(d + '\n')
            f5.write(e + '\n')
    with open(os.path.join(test_dir,"test.token.code"), "w") as f1,\
        open(os.path.join(test_dir,"test.token.nl"), "w") as f2,\
        open(os.path.join(test_dir,"test.token.pnl"), "w") as f3,\
        open(os.path.join(test_dir,"test.token.ast"), "w") as f4,\
        open(os.path.join(test_dir,"test.token.sbt"), "w") as f5:
        for a,b,c,d,e in zip(test_data[0], test_data[1], test_data[2], test_data[3], test_data[4]):
            f1.write(a + '\n')
            f2.write(b + '\n')
            f3.write(c + '\n')
            f4.write(d + '\n')
            f5.write(e + '\n')
