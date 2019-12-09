import os

projects=[]

for i in range(1,17):
    print("cat ", i,"result")
    path = '../result_file/'+ str(i) +'_exp_result/callgraph_info'
    for root, dir, files in os.walk(path):
        project_name = root.split('/')[-1]
        files_str = ""
        if len(files)!=0:
            for file in files:
                if file != project_name+ ".txt":
                    files_str += os.path.join(root, file)+" "
            if files_str != "":
                os.system("cat " + files_str + "> " + os.path.join(root, project_name + ".txt"))
                for file in files_str.split(" ")[0:-1]:
                    os.system("rm " + file)
                    