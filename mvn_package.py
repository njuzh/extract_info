import os
import time
import re

start = time.time()

exp_time = "_test"
projects_dir = "/root/repos/repos"+exp_time

all_projects_count = len(os.listdir(projects_dir))
mvn_projects_count = 0
for project_name in os.listdir(projects_dir):
    project_dir = os.path.join(projects_dir, project_name)
    if not "pom.xml" in os.listdir(project_dir):
        os.system("rm -r ", project_dir)
        print ("delete the project:", project_name)
    else:
        mvn_projects_count += 1
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>mvn package",project_name+">>>>>>>>>>>>>>")
        os.system("mvn package -DskipTests") 
end = time.time()
print("=================================")
print("all projects count:",all_projects_count)
print("package projects count:",mvn_projects_count)
print("time used:", end - start)
print("=================================")
