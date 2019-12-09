import time
import re
from collections import defaultdict
import csv
import json
import os
class MethodInfo:

    def __init__(self, read_path):
        self.read_path = read_path
    
    def read_initial_file(self):
        method_info_list = []
        csv.field_size_limit(500 * 1024 * 1024)
        with open(self.read_path, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                item_info = {}
                for key, value in zip(header, row):
                    item_info[key] = value
                    # the first line will be the summary doc
                    if key == "methodDoc":
                        item_info[key] = value.split('\n')[1].split('*')[1].strip()
                item_info["call_func_name"] = "/"
                item_info["call_func_parameter"] = "/"
                item_info["passed_comments"] = "/"
                 
                method_info_list.append(item_info)
            # for item in method_info_list:
            #     print(item['methodName'])
        return method_info_list

    
class CallGraph:

    def __init__(self, read_path):
        self.read_path = read_path

        
    def read_initial_file(self):
        method_invocation_list = []

        with open(self.read_path, "r") as f:
            lines = f.readlines()
            initial_line_count = len(lines)
            #filter some noise
            lines = [line.replace("M:","") for line in lines if line.startswith("M:")]
            lines = [line for line in lines if not '$' in line]
            line_count = len(lines)
            if line_count == 0:
                return []
            #print(initial_line_count, line_count)
            parameter_format = re.compile(r'[(](.*?)[)]', re.S)

            caller_line = lines[0].strip().split(' ')[0].replace(':','.')
            callee_line = (''.join(lines[0].strip().split(' ')[1].split(')')[1])+')').replace(':','.')
            last_caller_name = caller_line.split('(')[0]
            last_callee_name = callee_line.split('(')[0]
            last_caller_parameter = re.findall(parameter_format, caller_line)[0].split(',')
            last_callee_parameter = re.findall(parameter_format, callee_line)[0].split(',')
            
            last_caller = Caller(last_callee_name, last_caller_parameter)
            last_callee = Callee(last_callee_name, last_callee_parameter)
            callee_list = []
            callee_list.append(last_callee)
            for line in lines[1:]:
                caller_line = line.strip().split(' ')[0].replace(':','.')
                callee_line = (''.join(line.strip().split(' ')[1].split(')')[1])+')').replace(':','.')
                caller_name = caller_line.split('(')[0]
                callee_name = callee_line.split('(')[0]
                caller_parameter = re.findall(parameter_format, caller_line)[0].split(',')
                callee_parameter = re.findall(parameter_format, callee_line)[0].split(',')
                curr_caller = Caller(caller_name, caller_parameter)
                curr_callee = Callee(callee_name, callee_parameter)
                if curr_caller == last_caller:
                    if curr_callee not in callee_list:
                        callee_list.append(curr_callee)
                else:
                    method_invocation = MethodInvocation(last_caller, callee_list)
                    method_invocation_list.append(method_invocation)
                    last_caller = curr_caller
                    callee_list = []
                    callee_list.append(curr_callee)
            # for method_invocation in method_invocation_list:
            #     print("___caller:" + method_invocation.caller.name)
            #     for callee in method_invocation.callee:
            #         print("callee:" + callee.name + str(len(callee.parameters)))
            #         for parameter in callee.parameters:
            #             print("parameter:"+ parameter)
            return method_invocation_list
class MethodInvocation:

    def __init__(self, caller, callee):
        self.caller = caller
        self.callee = callee
    
class Caller:

    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
class Callee:

    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    # def __hash__(self):
    #     return hash(self.name)

def filter_doc(call_graph, method_info):
    #check if the name and the parameter are matching
    def is_equal(method_info, method_invocation):
        method_name = method_info["methodName"]
        invocation_name = method_invocation.name
        if method_name == invocation_name:
            if compare_parameter(method_info["methodParameterType"], method_invocation.parameters):
                return True
        return False
    def compare_parameter(doc_parameter, info_parameter):
        if doc_parameter == '/' and info_parameter == ['']:
            return True
        doc_parameter_count = doc_parameter.count('#')
        info_parameter_count = len(info_parameter)
        if doc_parameter_count != info_parameter_count:
            return False
        else:
            doc_parameter = doc_parameter.split('#')[0:-1]
            info_parameter = [item.split('.')[-1] for item in info_parameter]
            for a,b in zip(doc_parameter, info_parameter):
                if b not in a:
                    return False
            return True
    def find_matched_method_info(methods_info, call_info, flag):
        if flag == "CALLER":
            for method in methods_info:
                if is_equal(method, call_info):
                    return method
            return False
        elif flag == "CALLEE":
            callee_docs = []
            for callee in call_info:
                for method in methods_info:
                    #matching the passed callee doc
                    if is_equal(method, callee):
                        callee_info = {}
                        callee_info[callee.name] = method["methodDoc"]
                        callee_docs.append(callee_info)
            return callee_docs

    count = 0
    passed_comments_count = 0
    method_with_passed_comments = 0
    for method_invocation in call_graph:
        find_caller_result = find_matched_method_info(method_info, method_invocation.caller,"CALLER")
        if find_caller_result != False:
            count += 1
            callee_name =[callee.name for callee in method_invocation.callee]
            callee_parameter = [callee.parameters for callee in method_invocation.callee]
            find_caller_result["call_func_name"] = callee_name
            find_caller_result["call_func_parameter"] = callee_parameter 
            passed_docs = find_matched_method_info(method_info, method_invocation.callee, "CALLEE")
            if len(passed_docs)!=0:
                find_caller_result["passed_comments"] = passed_docs
                passed_comments_count += len(passed_docs)
                method_with_passed_comments += 1
    # print("match caller count:", count)
    # print("passed comments count:", passed_comments_count)
    return [passed_comments_count,method_with_passed_comments]

def wirte_json(method_info, path):
    with open(path, 'w') as f:
        json.dump(method_info, f)

if __name__=="__main__":
    localtime = time.asctime( time.localtime(time.time()) )
    all_java_files_count = 0
    all_method_count = 0
    all_good_method_count = 0
    all_callgraph_count = 0
    all_method_has_passed_comments = 0
    all_passed_comments = 0
    project_idx = 0
    failed_project_count = 0

    exp_start = 1
    exp_end = 16
    start = time.time()
    for i in range(exp_start, exp_end+1):
        call_info_dir = "../result_file/" + str(i) + "_exp_result/callgraph_info"
        method_info_dir = "../result_file/" + str(i) + "_exp_result/method_info"
        passed_info_dir = "../result_file/" + str(i) + "_exp_result/passed_dataset"
        #careful here!!
        if os.path.exists(passed_info_dir):
            os.system("rm -r "+ passed_info_dir)
        os.mkdir(passed_info_dir)
        for root, dir, files in os.walk(call_info_dir):
            project_name = root.split('/')[-1]
            if len(files) == 1:
                project_idx += 1
                print("project:",project_idx,">>>>>>>>>>>>generating json files for",project_name,">>>>>>>>>>")
                callgraph_path = os.path.join(root, files[0])
                callgraphs = CallGraph(callgraph_path)
                callgraph_info = callgraphs.read_initial_file()
                
                method_info_path = os.path.join(os.path.join(method_info_dir,project_name),os.listdir(os.path.join(method_info_dir,project_name))[0])
                methods = MethodInfo(method_info_path)
                methods_info = methods.read_initial_file()
                if len(callgraph_info) == 0 or len(methods_info)==0:
                    print("empty file!!")
                    failed_project_count +=1
                    continue
                all_java_files_count += int(method_info_path.split(".csv")[0].split('#')[1])
                all_method_count += int(method_info_path.split(".csv")[0].split('#')[2])
                all_good_method_count += int(method_info_path.split(".csv")[0].split('#')[3])
                all_callgraph_count += len(callgraph_info)
                # print("callgraph item count:", len(callgraph_info))
                # print("method count:", len(methods_info))

                passed_doc_count = filter_doc(callgraph_info, methods_info)[0]
                method_with_passed_comments = filter_doc(callgraph_info, methods_info)[1]
                all_method_has_passed_comments += method_with_passed_comments
                all_passed_comments += passed_doc_count

                if not os.path.exists(os.path.join(passed_info_dir,project_name)):
                    os.mkdir(os.path.join(passed_info_dir,project_name))
                wirte_json(methods_info, os.path.join(passed_info_dir,project_name,project_name+"#"+str(method_with_passed_comments)+"#"+str(passed_doc_count)+".json"))
                
    end = time.time()
    print("all projects count:",project_idx)
    print("all succeed projects count:",project_idx - failed_project_count)
    print("all java files count analyzed:", all_java_files_count)
    print("all methods count analyzed:", all_method_count)
    print("all good method count analyzed:", all_good_method_count)
    print("all callgraph count:",all_callgraph_count)
    print("all methods that has passed comments count:", all_method_has_passed_comments)
    print("all passed comments count:", all_passed_comments)
    with open("../log/pass_comments.log", "a+") as f:
        f.write("===============================\n")
        f.write("experiment NO: " + str(exp_start) +"-"+str(exp_end) + "\n")
        f.write("experiment time: " + str(localtime) + "\n")
        f.write("all projects count:" + str(project_idx) + "\n")
        f.write("all succeed projects count:" + str(project_idx - failed_project_count) + "\n")
        f.write("all java files count analyzed: " + str(all_java_files_count) + "\n")
        f.write("all methods count analyzed: "+ str(all_method_count) + "\n")
        f.write("all good method count analyzed: " + str(all_good_method_count) + "\n")
        f.write("all callgraph count: " + str(all_callgraph_count) + "\n")
        f.write("all methods that has passed comments count: " + str(all_method_has_passed_comments) + "\n")
        f.write("all passed comments count: " + str(all_passed_comments) + "\n")
        f.write("all time used: " +  str(end - start) +  "s\n" )
        f.write("===============================\n")

    