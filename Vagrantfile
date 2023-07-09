# on windows, disable VirtualisationBasedSecurity
# https://www.tomshardware.com/how-to/disable-vbs-windows-11

Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/bionic64"
  config.vm.provision :docker
  config.vm.provision :docker_compose
  config.vm.network "forwarded_port", guest: 5691, host: 5691
  config.vm.network "forwarded_port", guest: 3001, host: 3001
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 9092, host: 9092
  config.vm.network "forwarded_port", guest: 8501, host: 8501
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end
end