# on windows, disable VirtualisationBasedSecurity
# https://www.tomshardware.com/how-to/disable-vbs-windows-11
# https://stackoverflow.com/questions/65780506/how-to-enable-avx-avx2-in-virtualbox-6-1-16-with-ubuntu-20-04-64bit

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
    v.customize ['modifyvm', :id, '--nested-hw-virt', 'on']
    v.customize ['setextradata', :id, 'VBoxInternal/CPUM/IsaExts/AVX', '1']
    v.customize ['setextradata', :id, 'VBoxInternal/CPUM/IsaExts/AVX2', '1']
    v.customize ['modifyvm', :id, '--ioapic', 'on']
  end
end