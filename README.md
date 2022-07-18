# DB Explorer(DBE) command line tools
Better performance, higher efficiency and more features.

# Usage
Take three minutes to fully grasp!

## First, connect to server
> You can connect to one **DBE backend** server or **DBE Service Discovery Network**

```shell
dbe-cli connect [hostname | ip]
```

## The second and last step, type command
```shell
ls # ['ccubase', 'base', 'master', 'Co_1']

cd master # Now, you moved to 'master' node
pwd # master
```

You have completed all the beginner tutorials! You can now take a 
look at **Command cheat list**

# Command cheat list
### help [\<command>]  
DESCRIPTION  
&nbsp;&nbsp;
Print all available commands(listed below)

### connect [\<hostname | IP>]  
DESCRIPTION  
&nbsp;&nbsp;
Connect to DBE server, default is localhost

### cd [\<options>]  
DESCRIPTION  
&nbsp;&nbsp;
Change work node  
OPTIONS  
&nbsp;&nbsp; cd  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Change directory to **root**  
&nbsp;&nbsp; cd path  &nbsp;&nbsp;Change directory to **path**  
&nbsp;&nbsp; cd -  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Change directory to **previous path**

### pwd  
DESCRIPTION  
&nbsp;&nbsp;
Print currently node

### ls [-[an]]  
DESCRIPTION  
&nbsp;&nbsp;
print all directly keys under current node and attributes of current node  
OPTIONS  
&nbsp;&nbsp; ls     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;List sub nodes **and** attributes  
&nbsp;&nbsp; ls -n  &nbsp;&nbsp;&nbsp;List **only** sub nodes  
&nbsp;&nbsp; ls -a  &nbsp;&nbsp;&nbsp;List **only** attributes

### tree [-n] [\<node name | path>]  
DESCRIPTION  
&nbsp;&nbsp;
Print all nodes of current node in the form of tree  
OPTIONS  
&nbsp;&nbsp; tree -d  &nbsp;&nbsp;&nbsp;&nbsp;Limit the depth of recursion

### mkdir [-p \<path>] | \<node name>  
DESCRIPTION  
&nbsp;&nbsp;
Create new node  
OPTIONS  
&nbsp;&nbsp; mkdir -p  &nbsp;&nbsp;&nbsp;&nbsp;Make parent nodes if needed

### touch <node name>  
DESCRIPTION  
&nbsp;&nbsp;
Create new node

### rm [-[rf]] <node name | path>  
DESCRIPTION  
&nbsp;&nbsp;
Remove specific node(default current)

### cp [-r] path_I path_II:  
DESCRIPTION  
&nbsp;&nbsp;
Copy node or attribute

### mv path_I path_II:  
DESCRIPTION  
&nbsp;&nbsp;
Move node between different parent

### export:  
DESCRIPTION  
&nbsp;&nbsp;
Export new file

### more:  
DESCRIPTION  
&nbsp;&nbsp;
Lazy print result

### history:  
DESCRIPTION  
&nbsp;&nbsp;
Print all used commands

### grep:  
DESCRIPTION  
&nbsp;&nbsp;
Filter result

### find:  
DESCRIPTION  
&nbsp;&nbsp;
Filter result

### limit number:  
DESCRIPTION  
&nbsp;&nbsp;
Show limited results

### skip number:  
DESCRIPTION  
&nbsp;&nbsp;
Skip specific results

### exec filename:  
DESCRIPTION  
&nbsp;&nbsp;
Read and run commands in file

### mode [kv | dict]  
DESCRIPTION  
&nbsp;&nbsp;

### up key(↑):  
DESCRIPTION  
&nbsp;&nbsp;
Switch to prev command

### down key(↓):  
DESCRIPTION  
&nbsp;&nbsp;
Switch to later command

### ctrl+r:  
DESCRIPTION  
&nbsp;&nbsp;
Recursive search history command

### pipeline(|):  
DESCRIPTION  
&nbsp;&nbsp;
Connect multiple commands

### redirect([> | >>]):  
DESCRIPTION  
&nbsp;&nbsp;
Redirect result to file