import os
import time
import re

start = time.time()

exp_time = "3"
projects_dir = "/root/repos/repos"+exp_time

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

#sss
