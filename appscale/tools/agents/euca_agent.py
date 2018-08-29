import boto
import glob

from appscale.tools.appscale_logger import AppScaleLogger
from ec2_agent import EC2Agent
from urlparse import urlparse

__author__ = 'hiranya'
__email__ = 'hiranya@appscale.com'

class EucalyptusAgent(EC2Agent):
  """
  Eucalyptus infrastructure agent which can be used to spawn and terminate
  VMs in an Eucalyptus based environment.
  """

  # The version of Eucalyptus API used to interact with Euca clouds
  EUCA_API_VERSION = '2010-08-31'


  # A list of the credentials that we require users to provide the AppScale
  # Tools with so that they can interact with Eucalyptus clouds. Right now
  # it's the same as what's needed for EC2, with an extra argument indicating
  # where the Eucalyptus deployment is located.
  REQUIRED_EUCA_CREDENTIALS = list(EC2Agent.REQUIRED_EC2_CREDENTIALS) + \
    ['EC2_URL']


  # A list of credentials that we build our internal credential list from.
  REQUIRED_CREDENTIALS = REQUIRED_EUCA_CREDENTIALS


  def open_connection(self, parameters):
    """
    Initialize a connection to the back-end Eucalyptus APIs.

    Args:
      parameters  A dictionary containing the 'credentials' parameter

    Returns:
      An instance of Boto EC2Connection
    """
    credentials = parameters[self.PARAM_CREDENTIALS]
    access_key = str(credentials['EC2_ACCESS_KEY'])
    secret_key = str(credentials['EC2_SECRET_KEY'])
    ec2_url = str(credentials['EC2_URL'])
    result = urlparse(ec2_url)
    if result.port is not None:
      port = result.port
    elif result.scheme == 'http':
      port = 80
    elif result.scheme == 'https':
      port = 443
    else:
      self.handle_failure('Unknown scheme in EC2_URL: ' + result.scheme)
      return None

    if parameters['IS_VERBOSE']:
      debug_level = 2  # extremely verbose
    else:
      debug_level = 0  # the silent treatment

    return boto.connect_euca(host=result.hostname,
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key,
      port=port,
      path=result.path,
      is_secure=(result.scheme == 'https'),
      api_version=self.EUCA_API_VERSION, debug=debug_level)


  def does_zone_exist(self, parameters):
    """
    Queries Eucalyptus to see if the specified availability zone exists.

    Args:
      parameters: A dict that contains the zone to check for existence.
    Returns:
      True if the availability zone exists, False otherwise.
    """
    # Note that we can't use does_zone_exist in EC2Agent. There, if the image
    # doesn't exist, it throws an EC2ResponseError, but in Eucalyptus, it
    # doesn't (and returns None instead).
    conn = self.open_connection(parameters)
    zone = parameters[self.PARAM_ZONE]
    if conn.get_all_zones(zone):
      AppScaleLogger.log('Availability zone {0} does exist'.format(zone))
      return True
    else:
      AppScaleLogger.log('Availability zone {0} does not exist'.format(zone))
      return False

  def attach_disk(self, parameters, disk_name, instance_id):
    """ Attaches the Elastic Block Store volume specified in 'disk_name' to this
    virtual machine.

    Args:
      parameters: A dict with keys for each parameter needed to connect to AWS.
      disk_name: A str naming the EBS mount to attach to this machine.
      instance_id: A str naming the id of the instance that the disk should be
        attached to. In practice, callers add disks to their own instances.
    Returns:
      A regex that will match a symlink to the mount point.
    """

    try:
      conn = self.open_connection(parameters)
      AppScaleLogger.log('Attaching volume {0} to instance {1}'.format(
        disk_name, instance_id))
      conn.attach_volume(disk_name, instance_id, '/dev/sdc')
    except boto.exception.EC2ResponseError as exception:
      AppScaleLogger.log('An error occurred when trying to attach volume {0} '
          'to instance {1}.'.format(disk_name, instance_id))
      self.handle_failure('EC2 response error while attaching volume:' +
        exception.error_message)
    disk_glob = '/dev/disk/by-id/*euca-{}*'.format(disk_name)
    try:
      glob.glob(disk_glob)[0]
    except IndexError as e:
      self.handle_failure('Could not find disk name {} with regex {}'.format(
          disk_name, disk_glob), e)
