from config.reader.Config import Config
from config.reader.Node import Node
from config.reader.NICs import P2PNIC, WiFiNIC
from config.reader.NetworkConnection import NetworkConnection
from config.reader.AppConnections import AppConnections
from config.reader.AppConnectionsTypes import ControlAppConnectionPathType, ActuatorAppConnectionPathType
from config.reader.ConfigErrors import NodeWithNetworkIdAlreadyExistsInNetwork, NodeWithPowerIdAlreadyExistsInNetwork, \
    InvalidNetworkType, NetworkConnectionAlreadyExists, NodeInNetworkConnectionDoesHaveCorrectNIC, \
    NoAccessPointFoundInNetworkConnection, NoNonAccessPointFoundInNetworkConnection, \
    NodeInNetworkConnectionDoesNotExist, NodeInAppConnectionDoesNotExist, InvalidAppConnectionType, \
    NodeTooFarAwayFromAccessPoint
from config.reader.NetworkConnectionTypes import NetworkConnectionP2P, NetworkConnectionWiFi

if __name__ == '__main__':        
        file = open("TestFiles/ieee13.json")
        config = Config(file)
        config.read_config()
        print(config.get_network_connections_as_json())
        file.close()