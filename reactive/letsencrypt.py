from charms.reactive import when, when_not, set_state
from charmhelpers.core import hookenv
from charmhelpers import fetch
from charms import layer

import subprocess

@when_not('letsencrypt.installed')
def install_letsencrypt():
    fetch.add_source('ppa:certbot/certbot')
    fetch.apt_update()
    fetch.apt_install('certbot')
    hookenv.log("certbot installed","INFO")
    set_state('letsencrypt.installed')

def register_domains():
    ''' After forwarding the letsencrypt port, register current domains '''
    hookenv.log("letsencrypt register_domains() called","DEBUG")
    layer_config = layer.options('letsencrypt')
    charm_config = hookenv.config()
    if charm_config['letsencrypt-email']:
        email = "--email {}".format(charm_config['letsencrypt-email'])
    else:
        email = "--register-unsafely-without-email"
    return subprocess.call('certbot certonly \
                                   --staging \
                                   --standalone \
                                   --renew-by-default \
                                   --preferred-challenges http \
                                   --agree-tos \
                                   --no-eff-email \
                                   --http-01-port {port} \
                                   -d {domains} \
                                   --pre-hook "{pre}" \
                                   --post-hook "{post}" \
                                   {email}'.format(port = layer_config['port'],
                                                           pre = layer_config['pre-hook'],
                                                           post = layer_config['post-hook'],
                                                           email = email,
                                                           domains = charm_config['letsencrypt-domains']), shell=True)
