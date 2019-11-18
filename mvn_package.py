import os
import time
import re

start = time.time()

exp_time = "4"
localtime = time.asctime( time.localtime(time.time()) )
projects_dir = "/root/repos/repos"+exp_time
mvn_log_dir  = "/root/extract_info/mvn_log"
all_projects_count = len(os.listdir(projects_dir))
mvn_projects_count = 0
delete_projects = []
analyzed_projects = []
for project_name in os.listdir(projects_dir):
    project_dir = os.path.join(projects_dir, project_name)
    if not "pom.xml" in os.listdir(project_dir):
        delete_projects.append(project_name)
        os.system("rm -r " + project_dir)
    else:
        mvn_projects_count += 1
        analyzed_projects.append(project_name)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>mvn package",project_name+">>>>>>>>>>>>>>")
        os.system("cd " +project_dir + "; mvn package -DskipTests") 
end = time.time()

print("=================================")
print("all projects count:", all_projects_count)
print("package projects count:", mvn_projects_count)
print("package projects :", ' '.join(analyzed_projects))
print("delete no maven projects:", ' '.join(delete_projects))
print("time used:", end - start)
print("=================================")

with open(os.path.join(mvn_log_dir, "all_mvn_infomation.txt"), "a+") as f:
    f.write("===============================\n")
    f.write("experiment NO: " + exp_time + "\n")
    f.write("experiment time: " + str(localtime) + "\n")
    f.write("all projects count: " + str(all_projects_count) + "\n")
    f.write("package projects count: " + mvn_projects_count)
    f.write("package projects: " + ' '.join(analyzed_projects) + "\n")
    f.write("delete no maven projects: " + ' '.join(delete_projects)+ "\n")
    f.write("all time used: " +  str(end - start) +  "s\n" )
    f.write("===============================\n")
#sss
