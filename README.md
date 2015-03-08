## Agile Conf

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

Notes: You can specify the boilplate_repo by using --bo_repo or by set it in enviornment variable: AGC_BOIL.

#### 2. Walk thorugh the project.

A new project (build from single_ec2 boilplate) comes with following structure.

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

For example.

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


Variables defined in ```conf.yaml``` and ```project.yaml``` can be use in ```modules.yaml``` and templates.

Following is ```cfn/0_userdata.sh.tpl```

```bash
echo "hello world"
echo "This is [{{conf.name}}-{{conf.number}}] for project: {{project.product_fullname}}"
```

would be rendered into ```0_userdata.sh```

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
cfn/
	0_userdata.sh
	ec2.json
	module.yaml
create_stack.sh
kill_stack.sh
```

#### 4. Other commands



