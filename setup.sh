# Setup Berkeley Database
wget http://download.oracle.com/berkeley-db/db-4.8.30.NC.tar.gz
tar -xzf db-4.8.30.NC.tar.gz
cd db-4.8.30.NC/build_unix
sudo ../dist/configure --enable-cxx
sudo make
sudo make install
cd ../..

# Setup JPype
wget http://sourceforge.net/projects/jpype/files/JPype/0.5.4/JPype-0.5.4.2.zip
unzip JPype-0.5.4.2.zip
cd JPype-0.5.4.2
sudo -E python setup.py install
cd ..