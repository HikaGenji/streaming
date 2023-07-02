# on windows, disable VirtualisationBasedSecurity
# https://www.tomshardware.com/how-to/disable-vbs-windows-11

Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/bionic64"
  config.vm.provision :docker
  config.vm.provision :docker_compose
  config.vm.network "forwarded_port", guest: 4566, host: 4566
  config.vm.network "forwarded_port", guest: 5691, host: 5691
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 3001, host: 3001
  config.vm.network "forwarded_port", guest: 3002, host: 3002
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end
end