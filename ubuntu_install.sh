# sudo apt-get -y update
# sudo apt-get install -y git vim python-dev libxml2-dev libxslt-dev
virtualenv -p python2 py2-env
source activate py2-env/bin/activate
pip install zerorpc py-cpuinfo flask requests