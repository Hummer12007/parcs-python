# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
    config.vm.define "master", autostart: false do |master|
        master.vm.box = "bento/ubuntu-14.04"

        master.vm.network "public_network"
        master.vm.hostname = "master"

        master.vm.provider "virtualbox" do |vb|
            vb.memory = "1024"
        end

        master.vm.provision "shell", inline: <<-SHELL
            sudo apt-get -y update
            sudo apt-get install -y git vim python-dev libxml2-dev libxslt-dev python-pip
            sudo pip install netifaces pyro4 py-cpuinfo flask requests
            cd /home/vagrant
            rm -r parcs_py_project/
            echo "git clone https://github.com/mhodovaniuk/parcs_py_project.git" > clone_parcs.sh
            chmod +x clone_parcs.sh
            ./clone_parcs.sh
        SHELL
   end
   
   config.vm.define "worker1", autostart: false do |worker1|
        worker1.vm.box = "bento/ubuntu-14.04"

        worker1.vm.network "public_network"
        worker1.vm.hostname = "worker1"

        worker1.vm.provider "virtualbox" do |vb|
            vb.memory = "1024"
        end

        worker1.vm.provision "shell", inline: <<-SHELL
            sudo apt-get -y update
            sudo apt-get install -y git vim python-dev libxml2-dev libxslt-dev python-pip
            sudo pip install netifaces pyro4 py-cpuinfo flask requests
            cd /home/vagrant
            rm -r parcs_py_project/
            echo "git clone https://github.com/mhodovaniuk/parcs_py_project.git" > clone_parcs.sh
            chmod +x clone_parcs.sh
            ./clone_parcs.sh
        SHELL
   end

   config.vm.define "worker2", autostart: false do |worker2|
        worker2.vm.box = "bento/ubuntu-14.04"

        worker2.vm.network "public_network"
        worker2.vm.hostname = "worker2"

        worker2.vm.provider "virtualbox" do |vb|
            vb.memory = "1024"
        end

        worker2.vm.provision "shell", inline: <<-SHELL
            sudo apt-get -y update
            sudo apt-get install -y git vim python-dev libxml2-dev libxslt-dev python-pip
            sudo pip install netifaces pyro4 py-cpuinfo flask requests
            cd /home/vagrant
            rm -r parcs_py_project/
            echo "git clone https://github.com/mhodovaniuk/parcs_py_project.git" > clone_parcs.sh
            chmod +x clone_parcs.sh
            ./clone_parcs.sh
        SHELL
   end
end
