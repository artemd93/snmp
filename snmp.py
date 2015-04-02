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
    
    def get_oper(self, port):
        oid = OID.oper_st + '.' + port
        oper_st = self.snmpobj.snmp(oid, netsnmp.snmpget)[0]
        self.oper_st = translate(oper_st)

    def getall(self, st_type='oper'):
        self.ports_status = dict()
        for port in range(1, self.ports_count+1):
            self.ports_status[port] = self.get(st_type, str(port))

    def set(self, state, port=''):
        if not port:
            port = self.PORT
        oid = OID.adm_st
        if state == 'down':
            status = 2
        else:
            status = 1

        self.snmpobj.snmp(oid, netsnmp.snmpset, val=port,
                          status=status)
        self.set_st = str(self.snmpobj)

    def setall(self, state):
        for port in range(1, self.ports_count+1):
            print port
            self.set(state, str(port))
            if not self.set_st == 'Query OK':
                print('Port %s FAILED') % port

    def verify(self):
        self.getall('adm')
        for port in self.ports_status:
            if self.ports_status[port] == 'down':
                print('Port %s in administratively down' % port)

   def reset(self):
        self.set('down')
        self.set('up')

    def save(self):
        if self.SWITCH == 'DES-1210-52':
            oid = OID.save_52
        elif self.SWITCH == 'DES-1210-28':
            oid = OID.save_28
        else:
            raise SnmpErrorException('Wrong switch name')

        self.set_st = self.snmpobj.snmp(oid, netsnmp.snmpset,
                                        val='0', status=1)
        self.set_st = set_decode(self.set_st)

    def restart(self):
        if self.SWITCH == 'DES-1210-52':
            oid = OID.restart_52
        elif self.SWITCH == 'DES-1210-28':
            oid = OID.restart_28
        else:
            raise SnmpErrorException('Wrong switch name')

        self.set_st = self.snmpobj.snmp(oid, netsnmp.snmpset,
                                        val='0', status=1)
        self.set_st = set_decode(self.set_st)

    def get_ports_count(self):
        if self.SWITCH == 'DES-1210-52':
            self.ports_count = 48
        elif self.SWITCH == 'DES-1210-28':
            self.ports_count = 24
        else:
            raise SnmpErrorException('Wrong switch name')
            
    def __unicode__(self):
        sep = '=' * 28
        str_form = '%s\n%s\nSWITCH: %s PORT: %s\n' % (sep,
                                                      self.SWITCH,
                                                      self.IP,
                                                      self.PORT)
        for attr in Data.attrs:
            if hasattr(self, attr):
                str_form += '%s %s\n' % (Data.attrs[attr],
                                         getattr(self, attr))
        return str_form + sep

    def __str__(self):
        return unicode(self).encode('utf-8')


class Snmp(object):
    def __init__(self, host='localhost', version=1, community='public'):
        self.host = host
        self.version = version
        self.community = community

    def snmp(self, oid, snmpx, val=False, status=False):
        if snmpx is netsnmp.snmpset:
            oid = netsnmp.Varbind(oid, val, status, 'INTEGER')
        else:
            oid = netsnmp.Varbind(oid)
        res = snmpx(oid, Version=self.version, DestHost=self.host,
                    Community=self.community)
        self.last_query = res
        return res

    def __str__(self):
        if self.last_query == 1:
            return 'Query OK'
        else:
            return 'Query ERROR'

if __name__ == '__main__':

    print('To be defined')
