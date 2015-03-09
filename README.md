## Agile Conf Document (WIP)

[agile_conf](https://github.com/tly1980/agile_conf) - A config files (in [YAML](http://yaml.org) format) and template engine ([Jinja2](http://jinja.pocoo.org)) based configuration compile / management tool to make DevOp tasks (or maybe 1,000 other things) easier.

### Motivation

A lot of work of DevOps is about configs / deployment script generation and management.

One can easily implement script using ["sed"](http://en.wikipedia.org/wiki/Sed) to generate the configs / deployment scripts.
However, ["sed"](http://en.wikipedia.org/wiki/Sed) is far away from a perfect tool when you want to do some slightly complicated find / replace.
From my expierence, modern [Templating processor](http://en.wikipedia.org/wiki/Template_processor) does a much better job in:

**translating the variables into any forms of text-based outputs** (HTML, XML, JSON, YAML, INI, ..., etc.).

Powered by ([Jinja2](http://jinja.pocoo.org)), [agile_conf](https://github.com/tly1980/agile_conf) supports all the features that is built-in with ([Jinja2](http://jinja.pocoo.org)) templating, such as:
template inhertitance, include, .etc.

On top of that, [agile_conf](https://github.com/tly1980/agile_conf) comes with some useful filters for DevOps purpose:

1. jsonify
2. aws_userdata     
(it can translate [AWS userdata](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html) into [cloudformation stack template](http://aws.amazon.com/cloudformation/aws-cloudformation-templates/))
3. yamlify

Other than that, I believe that we should be serious about config / deployment scripts. Rather than doing the scripts / config generation with the execution altogether at run time, I prefer that we can have the compiled scripts / configuration by hands **before** executing it. 

So that we can review the deployment scripts / config before running them, to gain clear idea on what is going to happen and avoid the surpise you don't want.

I also believe we should manage those compiled deployment scripts / configurations in [git](http://git-scm.com) or any other SCM, so that we can treat them seriously just like we usually does with our code.
And because they're managed by SCM, we will have full history, diff between changes, and permissions control.


### Basic workfolw

0. Create a project, and use [git](http://git-scm.com) or other SCM to manage it.
1. Define your variable and templates. 
2. Compile artifacts: any text-based config / scripts.
3. Commit your changes (variable, templates and the compiled scripts and configs) to the [git](http://git-scm.com) or other SCM repository.
4. Use Bamboo or Jenkins to check out the compiled scripts and configs and execute them.
Or, you can always run the scripts locally as long as you have the permissions.
5. Retired your compiled scripts and configs if you don't need them (You should destroy the resources accordingly, using the pre-compiled destroy scripts.)

### Install

Use [PIP](https://pip.pypa.io/en/latest/quickstart.html) to install it.

```
pip install agile-conf
```
If you don't have [PIP](https://pip.pypa.io/en/latest/quickstart.html), please [install](https://pip.pypa.io/en/latest/installing.html) it first.

After the installation, you can run ```agc --help``` to verify.

### Getting started
```agc``` is the main commandline tool of [agile_conf](https://github.com/tly1980/agile_conf).

0. Clone the boilplate locally.
```
git clone https://github.com/tly1980/agile_conf_boilplate.git ~/workspace/agile_conf_boilplate
```

You don't have to use this boilplate repository, you can create your own boilplate repository by using same directory structure.


#### 1. Create a new project by using the boilplate. 

```
$ agc create single_ec2 my_ec2 --bo_repo=~/workspace/agile_conf_boilplate/
creating project: my_ec2
using boilerplate: /Users/minddriven/workspace/agile_conf_boilplate/single_ec2
```

Notes: You can specify the boilplate_repo with ```--bo_repo```, or set it in enviornment variable: ```AGC_BOIL```.

#### 2. Walk thorugh the project.

```my_ec2``` project (build from single_ec2 boilplate) comes with following structure.

Please read through the comments.

```
my_ec2
	/_script
	/cfn
		module.yaml  # the variables specifically for cfn module
		ec2.josn.tpl # template of cloudformation script
		0_userdata.sh.tpl # template of the userdata. 
						  # Rendering happended alphabatically
						  # '0_' prefix makes it the first one to be render.
	conf_perf.yaml   # config for 'perf' performance test builds.
	conf_prod.yaml   # config for 'prod' production builds.
	conf_uat.yaml    # config for 'uat' user user acceptance builds.
	Makefile
	project.yaml    # the common variables 
	                # that can use across 
	                # diffeent modules
	README.md
```

In project folder, any sub-folders do **NOT** has "_" prefix is a module. Each module can have its own templates. 
Inside the module, any file that has ".tpl" postfix in the name would be rendered.

The order of rendering is alphabetical. This is a simple way to avoid circulating dependencies.

Common template variables are defined in ```project.yaml```, ```conf.yaml```.

Module specific variables are defined in ```module.yaml```.


Variables defined in ```conf.yaml```, can be referenced in ```projects.yaml``` and ```module.yaml``` and templates.

In the single_ec2 projects, it has mupltiple conf.yaml for different enviornments.
```conf_uat.yaml```, ```conf_prod.yaml``` and ```conf_prod.yaml```. When you run the command, you should run it with ```--conf``` options.


With a ```conf_uat.yaml```
```yaml
name: uat
netenv: uat   # will deploy to uat subnets
number: 1
```

Following is a line in ```project.yaml```
```yaml
product_fullname: hello-ec2-{{ conf.name }}-{{ conf.number }}
```

would be rendered into

```yaml
product_fullname: hello-ec2-uat-1
```

Variables defined in ```conf.yaml``` and ```project.yaml``` can be use in ```${MODULE}/module.yaml``` and templates.

If you want to see the exact value used in the templates:
USE ```inspect``` command.

```
$ agc inspect --conf conf_uat.yaml
```

Output would be:
```
with [conf=conf_uat.yaml]
[conf]
name: uat
netenv: uat
number: 1


[project]
instance_type:
  perf: m3.large
  prod: m3.medium
  uat: t2.micro
product_fullname: hello-ec2-uat-1


[cfn]
image_id: ami-d50773ef
instance_type: t2.micro
key_name: my-key
netenv: uat
subnet_id:
  prod: subnet-prodsubnet
  uat: subnet-uatsubnet
subnet_security_groups:
  prod:
  - sg-prod1
  - sg-prod2
  uat:
  - sg-uat1
  - sg-uat2
subnet_sg_group: front
tags:
- Key: Name
  Value: hello-ec2-uat-1
- Key: Environment
  Value: uat
```

### 3. Create a config build.

Run follow command will generate a build. 
You must provide the conf file with ```--conf```, so that command tool knows which conf file to use.

```
agc build --conf conf_uat.yaml
```

It will generate a new folder in ```_builds/{conf.name}/{conf.number}```.

If the content inside ```conf_uat.yaml``` is following:

```yaml
name: uat
netenv: uat   # will deploy to uat subnets
number: 1
```

You would have a folder ```_builds/uat/1``` with following layout:

```
cfn/             # all are from cfn/*.tpl
	0_userdata.sh
	ec2.json
	module.yaml
create_stack.sh  # compiled from _script/create_stack.sh.tpl
kill_stack.sh    # compiled from _script/kill_stack.sh.tpl
```

### 4. filters

[agile_conf](https://github.com/tly1980/agile_conf) built-in jinja2 filters.


Here is the example of ```aws_userdata``` filter from the ```single_ec2``` boilplate project.

```bash
echo "hello world"
echo "This is [{{conf.name}}-{{conf.number}}] for project: {{project.product_fullname}}"
```

It would be rendered into:
```bash
echo "hello world"
echo "This is [uat-1] for project: hello-ec2-uat-1"
```

In ```ec2.json.tpl``` we have a following code. 

```
"UserData": {{ [_BUILD_DST_FOLDER, "0_userdata.sh"] |aws_userdata }},
```

It is using a ```aws_userdata``` filter to turn ```0_userdata.sh``` into following code.

```_BUILD_DST_FOLDER``` is the output destination folder of the module, exactly where the ```0_userdata.sh``` located.

And you can see the shell script is rendred into cloudformation json structure:

```
"UserData": {
    "Fn::Base64": {
        "Fn::Join": [
            "",
            [
                "echo \"hello world\"\n",
                "echo \"This is [uat-1] for project: hello-ec2-uat-1\"\n"
            ]
        ]
    }
},
```

Another filter is ```jsonify```.

In ```cfn/module.yaml```, tags are defined in following value:

```yaml
tags:
  - Key: Name
    Value: {{ project.product_fullname }}
  - Key: Environment
    Value: {{ conf.netenv }}
```

In ```cfn/ec2.json.tpl```, it is how ```tags``` being used:

```
"Tags": {{ tags|jsonify }}
```

It would be rendered into following:

```
"Tags": [
		{"Key": "Name", "Value": "hello-ec2-uat-1"},
		{"Key": "Environment", "Value": "uat"}
	]
```

### Commands

**Command: build**

Compile the variables into 


```
agc build --conf conf_xxx.yaml
```

**Command: inspect**

Print out all the variables, would be very useful for debugging

```
agc inspect --conf conf_xxx.yaml
```

**Command: inspect**


```
agc inspect --conf conf_xxx.yaml
```

**Shortcut: using**

If you put following shell script in your BASH rc file,  

```bash
using() {
    envcmd="env AGC_CONF=conf_$1.yaml"
    shift
    actual_cmd="$@"
    $envcmd $actual_cmd
}
```

you will have a very convinient short cut to switch different conf_xxx.yaml.


```
using uat agc inspect
```

```
using uat agc build
```

It is particular useful to do it with Makefile.

Supposed you have following a Makefile.

```Makefile
build_uat:
	agc build --conf conf_uat.yaml

build_prod:
	agc build --conf conf_prod.yaml

build_perf:
	agc build --conf conf_prod.yaml

```

With shortcut ```using```, you could have a Makefile like following:

```Makefile
build_uat:
	agc build
```

So you can switch between different conf_xxx.yaml by:


1. ```using uat make build```
2. ```using prod make build```
3. ```using perf make build```

**PS**: ```using``` can work with all the command with ```--conf``` options.

**Command: create**

To create a project from boilerplate repository.

```
agc create ${bo_name} ${project}
```

Before you run this command, you should set enviornment variable ```AGC_BOIL```,  
or use it with ```--bo_repo``` with it.

> --bo_repo or AGC_BOIL can only be set to point to a local path. 
> You cannot put it GIT/HTTP URL to it, yet ... :)


**Command: id**

```agc id --conf conf_uat.yaml``` or ```using uat agc id```

Will output:

```{conf_name}/{conf_number}```

**Command: where**
```agc id --conf conf_uat.yaml``` or ```using uat agc where```

Will output the exact location where the build is gonna to be.

e.g.:
```
$ using uat agc where
/Users/minddriven/workspace/play_agile_conf/my_ec2/_builds/uat/1
```




