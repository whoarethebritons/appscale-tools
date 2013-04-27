# Script for installing AppScale Tools dependencies by source for Python2.7.
export PYTHON=python2.7
if [ -d "/usr/local/Python-2.7.3/" ]
then
  echo "Setting alias for Python2.7"
  export PYTHON=/usr/local/Python-2.7.3/python
fi

if [ -x $PYTHON ]
then
  echo "Found python2.7"
else
  echo "Did not find python2.7"
  exit 1
fi

# Install setup tools.
curl https://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz#md5=7df2a529a074f613b509fb44feefe74e > setuptools-0.6c11.tar.gz
tar zxvf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
$PYTHON setup.py install
cd ..

# Install termcolor.
curl https://pypi.python.org/packages/source/t/termcolor/termcolor-1.1.0.tar.gz#md5=043e89644f8909d462fbbfa511c768df > termcolor-1.1.0.tar.gz
tar zxvf termcolor-1.1.0.tar.gz
cd termcolor-1.1.0
$PYTHON setup.py install
cd ..

# Install boto.
git clone https://github.com/boto/boto.git
cd boto
$PYTHON setup.py install
cd ..

# Install PyYAML.
curl http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz > PyYAML-3.10.tar.gz
tar zxvf PyYAML-3.10.tar.gz
cd PyYAML-3.10
$PYTHON setup.py install
cd ..

# Install SOAPpy.
git clone https://github.com/kiorky/SOAPpy.git
cd SOAPpy
$PYTHON setup.py install
cd ..

# Remove downloaded files.
rm -fdr PyYAML-3.10.tar.gz setuptools-0.6c11.tar.gz termcolor-1.1.0.tar.gz setuptools-0.6c11 termcolor-1.1.0 boto PyYAML-3.10 SOAPpy
