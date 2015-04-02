import netsnmp
from settings import Data, OID
from utils import *
from error import SnmpErrorException


class SnmpBased(object):
    def __init__(self, ip, port=''):
        self.IP = ip
        self.PORT = port
        self.snmpobj = Snmp(host=self.IP, version=Data.snmp['version'],
                            community=Data.snmp['community'])
        self.SWITCH = self.snmpobj.snmp(OID.sysname, netsnmp.snmpget)[0]
        if self.SWITCH is None:
            raise SnmpErrorException('Wrong IP')
        self.SWITCH = self.SWITCH.split(' ')[0]
        self.get_ports_count()

    def get(self, st_type='both', port=''):
        if not port:
            port = self.PORT
        if st_type == 'adm':
            self.get_adm(port)
            return self.adm_st
        elif st_type == 'oper':
            self.get_oper(port)
            return self.oper_st
        else:
            self.get_adm(port)
            self.get_oper(port)

    def get_adm(self, port):
        oid = OID.adm_st + '.' + port
        adm_st = self.snmpobj.snmp(oid, netsnmp.snmpget)[0]
        self.adm_st = translate(adm_st)
