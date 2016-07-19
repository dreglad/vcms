# Instalación #



## Requerimientos ##

* Vagrant (https://www.vagrantup.com)
* Virtualbox (https://www.virtualbox.org)


## Instalación Local ##

Clonar repositorio
```
#!bash

$ git clone https://github.com/dreglad/vcms
$ cd vcms
```

Crear, correr y aprovisionar máquina virtual
```
#!bash

$ vagrant up
```


## Deployment en producción ##

La Jornada
```
#!bash

$ ansible-playbook -i provisioning/lajornada_inventory.ini provisioning/playbook.yml

```


Globovisión
```
#!bash

$ ansible-playbook -i provisioning/gv_inventory.ini provisioning/playbook.yml

```


teleSUR English
```
#!bash

$ ansible-playbook -i provisioning/telesurenglish_inventory.ini provisioning/playbook.yml

```
