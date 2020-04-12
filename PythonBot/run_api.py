from api.api import setup
from secret.secrets import APIAddress, APIPort

if __name__ == '__main__':
    setup().run(host=APIAddress, port=APIPort, debug=False)
