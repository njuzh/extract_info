import os
import time
projects_dir = "../repos/repos2"
exp_time = "2"

result_dir = "/root/result/"+ exp_time +"_exp_result"
jars_dir = "/root/result/"+ exp_time +"_exp_result/project_jars"
csv_dir = "/root/result"+ exp_time +"_exp_result/method_info"
txt_dir ="/root/result"+ exp_time +"_exp_result/callgraph_info"
log_dir = "/root/result"+ exp_time +"_exp_result/log"

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

def is_legal_jar(jar_name):
    illegal_str = ["source", "javadoc", "example", "test", "dependencies"]
    for str in illegal_str:
        if str in jar_name:
            return False
    return True

os.system("script " + os.path.join(log_dir, "log.log") )
analyzed_count = 0
projects_count = len(os.listdir(projects_dir))
start = time.clock()
missed_projects = []
for project_name in os.listdir(projects_dir):
    project_dir = os.path.join(projects_dir, project_name)
    new_jar_path = os.path.join(jars_dir, project_name)
    new_csv_path = os.path.join(csv_dir, project_name)
    new_txt_path = os.path.join(txt_dir, project_name)
    
    jars = []
    for root, dir, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".jar")  and is_legal_jar(file):
                file_dir = os.path.join(root, file)
                jars.append(file_dir)
    if len(jars)!=0:
        analyzed_count += 1
        if not os.path.exists(new_jar_path):
            os.mkdir(new_jar_path)
        if not os.path.exists(new_csv_path):
            os.mkdir(new_csv_path)
        if not os.path.exists(new_txt_path):
            os.mkdir(new_txt_path)
        print(">>>>Project No:", analyzed_count)
        print(">>>>extracting infomation for", project_name)
        
        #extract method infomation
        os.system("java -jar "+ jdt_dir + " " + project_dir)
        csv_file = [file for file in os.listdir(os.getcwd()) if file.endswith('.csv')][0]
        os.system("mv " + csv_file + " " + new_csv_path)
        
        #extract callgraph infomation
        for jar in jars:
            os.system("cp " + jar + " " + new_jar_path)
            print(">>>>extracting callgraph info for" + jar.split('/')[-1] + "*********")
            os.system("java -jar " + javacg_dir + " " + jar + " > " + os.path.join(new_txt_path, jar.split('/')[-1] + ".txt"))
        print(">>>>extracting callgraph infomation done.")
    else:
        missed_projects.append(project_name)
    
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("")


end = time.clock()
print("===============================")
print("all projects count:", projects_count)
print("analyzed projects count:", analyzed_count)
if projects_count != analyzed_count:
    print("missed projects:", str(missed_projects))
print("all time used:", end - start)
print("===============================")
