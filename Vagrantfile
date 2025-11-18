# -*- mode: ruby -*-
# vi: set ft=ruby :



Vagrant.configure("2") do |config|
  #config.vm.box = "ktr/mininet"
  config.ssh.insert_key = false
  config.vbguest.auto_update = false
  config.vm.define "webserver" do |web_config|
    web_config.vm.box = "ubuntu/trusty64"
    web_config.vm.hostname = "webserver"
    web_config.vm.network "private_network", ip: "192.168.56.21"
    web_config.vm.network "forwarded_port", guest: 80, host: 8080
    web_config.vm.provider "virtualbox" do |vb|
      vb.name = "webserver"
      opts = ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize opts
      vb.memory = "256"
    end
    web_config.vm.provision "shell", path: "bootstrap_web.sh"
  end

  config.vm.define "client" do |web_config|
    web_config.vm.box = "ubuntu/trusty64"
    web_config.vm.hostname = "client"
    web_config.vm.network "private_network", ip: "192.168.56.11"
    web_config.vm.provider "virtualbox" do |vb|
      vb.name = "client"
      opts = ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize opts
      vb.memory = "256"
    end
  end
end
