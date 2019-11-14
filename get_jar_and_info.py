import os
import time
projects_dir = "../repos/repos2"
jars_dir = "../2_exp_result/project_jars"
csv_dir = "../2_exp_result/method_info"
txt_dir ="../2_exp_result/callgraph_info"
log_dir = "../2_exp_result/log"

jdt_dir = "../java_jars/jdt-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
javacg_dir = "../java_jars/javacg-0.1-SNAPSHOT-static.jar"

def is_legal_jar(jar_name):
    illegal_str = ["source", "javadoc", "example", "test", "dependencies"]
    for str in illegal_str:
        if str in jar_name:
            return False
    return True
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
        print("extracting method info for", project_name, "PROJECT NO:", analyzed_count)
        os.system("java -jar "+ jdt_dir + " " + project_dir)
        os.system("mv "+ project_name + "_javadoc.csv " + new_csv_path)
        print ("mv "+ project_name + "_javadoc.csv " + new_csv_path)
        for jar in jars:
            print("cp " + file + " to jars dir" )
            os.system("cp " + jar + " " + new_jar_path)
            print("extracting callgraph info for" + jar.split('/')[-1] + "*********")
            os.system("java -jar " + javacg_dir + " " + jar + " > " + os.path.join(new_txt_path, jar.split('/')[-1] + ".txt"))
            print("extracting callgraph infomation done.")
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
