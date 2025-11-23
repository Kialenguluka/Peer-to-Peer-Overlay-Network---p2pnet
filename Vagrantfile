# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vbguest.auto_update = false

  # 1. SERVIDOR DE PEERS (Centralizado - UDP)
  config.vm.define "peer_server" do |srv|
    srv.vm.box = "ubuntu/focal64"
    srv.vm.hostname = "peer-server"
    srv.vm.network "private_network", ip: "192.168.56.21" # IP Obrigatório [cite: 49]
    srv.vm.synced_folder ".", "/vagrant", disabled: false
    srv.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end

  # 2. PEER A (Cliente 1)
  config.vm.define "peer_A" do |pa|
    pa.vm.box = "ubuntu/focal64"
    pa.vm.hostname = "peer-A"
    pa.vm.network "private_network", ip: "192.168.56.22"
    pa.vm.synced_folder ".", "/vagrant", disabled: false
    pa.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end
  
  # 3. PEER B (Cliente 2 - Para testar conexões entre peers depois)
  config.vm.define "peer_B" do |pb|
    pb.vm.box = "ubuntu/focal64"
    pb.vm.hostname = "peer-B"
    pb.vm.network "private_network", ip: "192.168.56.23"
    pb.vm.synced_folder ".", "/vagrant", disabled: false
    pb.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end
  end
end