
## Prerequisite
Install packer
## How to use packer

format packer file
```
packer fmt ami.pkr.hcl
```

validate
```
packer validate ami.pkr.hcl
```

build
```
packer build ami.pkr.hcl
PACKER_LOG=1 packer build ami.pkr.hcl
```

build with variable
```
PACKER_LOG=1 packer build -var 'source_ami=demo_ami' -var 'subnet_id=default_vpc_id' ami.pkr.hcl
```
