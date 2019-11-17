import os
import time
import re
start = time.time()

exp_time = "2"
projects_dir = "/root/repos/repos"+exp_time
missed_projects_dir = "/root/repos/repos_man"
result_dir = "/root/git/result/"+ exp_time +"_exp_result"
jars_dir = "/root/project_jars"
csv_dir = "/root/git/result/"+ exp_time +"_exp_result/method_info"
txt_dir ="/root/git/result/"+ exp_time +"_exp_result/callgraph_info"
log_dir = "/root/git/result/"+ exp_time +"_exp_result/log"

if not os.path.exists(result_dir):
    os.mkdir(result_dir)
if not os.path.exists(jars_dir):
    os.mkdir(jars_dir)
if not os.path.exists(csv_dir):
    os.mkdir(csv_dir)
if not os.path.exists(txt_dir):
    os.mkdir(txt_dir)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

jdt_dir = "/root/java_jars/jdt-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
javacg_dir = "/root/java_jars/javacg-0.1-SNAPSHOT-static.jar"

def is_legal_jar(file_name, project_name):
    if not file_name.endswith(".jar"):
        return False

    illegal_strs= ["source", "javadoc", "example", "test", "dependencies", "original"]
    for illegal_str in illegal_strs:
        if illegal_str in file_name:
            return False

    file_name_str = ''.join(re.findall(r'[a-zA-Z0-9]', file_name)).lower()
    project_name_str =  ''.join(re.findall(r'[a-zA-Z0-9]', project_name)).lower()
    if not project_name_str in file_name_str: 
        return False
    
    return True

#os.system("script " + os.path.join(log_dir, "log.log") )
analyzed_project_count = 0
projects_count = len(os.listdir(projects_dir))
analyzed_jar_count = 0
missed_projects = []
for project_name in os.listdir(projects_dir):
    project_dir = os.path.join(projects_dir, project_name)
    new_jar_path = os.path.join(jars_dir, project_name)
    new_csv_path = os.path.join(csv_dir, project_name)
    new_txt_path = os.path.join(txt_dir, project_name)
    
    jars = []
    for root, dir, files in os.walk(project_dir):
        for file in files:
            if is_legal_jar(file, project_name):
                file_dir = os.path.join(root, file)
                jars.append(file_dir)
    if len(jars)!=0:
        analyzed_project_count += 1
        analyzed_jar_count += len(jars)
        if not os.path.exists(new_jar_path):
            os.mkdir(new_jar_path)
        if not os.path.exists(new_csv_path):
            os.mkdir(new_csv_path)
        if not os.path.exists(new_txt_path):
            os.mkdir(new_txt_path)
        print(">>>>Project No:", analyzed_project_count)
        print(">>>>extracting infomation for ", project_name)
        
        #extract method infomation
        os.system("java -jar "+ jdt_dir + " " + project_dir)
        csv_file = [file for file in os.listdir(os.getcwd()) if file.endswith('.csv')][0]
        os.system("mv " + csv_file + " " + new_csv_path)
        
        #extract callgraph infomation
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print(">>>>extracting callgraph infomation of", len(jars), "jars")
        for jar in jars:
            os.system("cp " + jar + " " + new_jar_path)
            print(">>>>extracting callgraph info for " + jar.split('/')[-1])
            os.system("java -jar " + javacg_dir + " " + jar + " > " + os.path.join(new_txt_path, jar.split('/')[-1] + ".txt"))
        print(">>>>extracting callgraph infomation done.")
    else:
        missed_projects.append(project_name)
        os.system("mv " + project_dir + " " + missed_projects_dir)
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("")


end = time.time()
print("===============================")
print("all projects count:", projects_count)
print("analyzed projects count:", analyzed_project_count)
print("analyzed jars count:", analyzed_jar_count)
if projects_count != analyzed_project_count:
    print("missed projects:", str(missed_projects))
print("all time used:", end - start, "s")
print("===============================")
