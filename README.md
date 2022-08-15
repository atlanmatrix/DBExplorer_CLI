# DB Explorer(DBE) command line tools
Better performance, higher efficiency and more features.

## Installation
```shell
pip install dbe-cli
```

> If you want to install this program on Windows, you should install pyreadline 
> first.


## Usage
Take three minutes to fully grasp!

### First, launch dbe_cli
> Attention: You need to run an DBE server first

```shell
python -m dbe_cli
```

### Second, connect to one database host
> Default host is the DBE server, not the machine which runs dbe_cli

```shell
connect localhost
```

### The third and last step, type command
> You can use **TAB** for autocompletion

```shell
ls # ['ccubase', 'base', 'master', 'Co_1']

cd master # Now, you moved to 'master' node
pwd # master
```

You have completed all the beginner tutorials! You can now take a 
look at **Command cheat list**

## More...
You can type `?` and press `Enter` key to get help information for the program. 

If you want to know how to use a specific 
command, use `? <command_name>`
