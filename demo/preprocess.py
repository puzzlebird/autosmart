from scapy.all import *
import os
import pandas as pd
import time
from joblib import Parallel, delayed

def log_time(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        print("Time: %f " % (end_time - start_time))
        return result

    return wrapper


def getPID(layer_names):

    return '_'.join(sorted(layer_names))


def getPIDFromPkt(p):

    layer_names = [layer.name for i, layer in enumerate(expand(p), 0)]
    return getPID(layer_names)


def generalLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'src' in key or 'dst' in key:
            # TODO
            # src = 2002:dca5:f85::dca5:f85 [6to4 GW: 220.165.15.133] from ips_2002-dca5-f85--dca5-f85_20190131_202924_543872217.pcap
            fields = item.split('.') if '.' in item and ':' not in item else item.split(':') 
            for i in range(len(fields)):
                data['_'.join([layer.name, key, str(i)])] = fields[i]
        elif 'data' in key or 'load' in key:
            data['_'.join([layer.name, key])] = hash(item)
        elif 'options' in key:
            for k, i in dict(item).items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def bootpLayer(layer):
    data = {}
    for key, item in layer.fields.items():
        if any([s in key for s in ['chaddr', 'sname', 'file']]):
            data['_'.join([layer.name, key])] = hash(item)
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def dhcpOptionLayer(layer):
    data = {}
    for key, item in layer.fields.items():
        if 'options' in key:
            new_item =  [i for i in item if type(i) == tuple]
            new_item = dict(new_item)
            for k, i in new_item.items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def dnsLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'qd' == key or 'ar' == key:
            if type(item) == list:
                item = item[0] # TODO
            for k, i in item.fields.items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def snmpLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'PDU' in key:
            for k, i in item.fields.items():
                if isinstance(item, ASN1_Object):
                    data['_'.join([layer.name, key, k])] = i.val
                elif 'varbindlist' in key:
                    data['_'.join([layer.name, key, k])] = i[0].oid.val # TODO
        elif isinstance(item, ASN1_Object):
            data['_'.join([layer.name, key])] = item.val
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def icmpv6NDNLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'tgt' in key:
            fields = item.split('.') if '.' in item else item.split(':')
            for i in range(len(fields)):
                data['_'.join([layer.name, key, str(i)])] = fields[i]
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def icmpv6NDOSLLALayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'lladdr' in key:
            fields = item.split('.') if '.' in item else item.split(':')
            for i in range(len(fields)):
                data['_'.join([layer.name, key, str(i)])] = fields[i]
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def ikeTransLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'transforms' in key:
            for k, i in dict(item).items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def ikeProposalLayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'trans' == key:
            item = ikeTransLayer(item)
            for k, i in item.items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def isakmpSALayer(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'prop' in key:
            item = ikeProposalLayer(item)
            for k, i in item.items():
                data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


def ipv6EH(layer):

    data = {}
    for key, item in layer.fields.items():
        if 'options' in key:
            if type(item) == list:
                for i in item:
                    new_item = generalLayer(i)
                    for k, i in new_item.items():
                        data['_'.join([layer.name, key, k])] = i
            else:
                item = generalLayer(item)
                for k, i in item.items():
                    data['_'.join([layer.name, key, k])] = i
        else:
            data['_'.join([layer.name, key])] = item
        
    return data


all_layers = { 
    'IPv6 Extension Header - Hop-by-Hop Options Header': ipv6EH, 
    'Raw': generalLayer, 
    'NTPHeader': generalLayer, 
    'ICMPv6 Packet Too Big': generalLayer, 
    'ICMPv6 Neighbor Discovery - Neighbor Advertisement': icmpv6NDNLayer, 
    'ICMPv6 Echo Reply': generalLayer, 
    'TCP in ICMP': generalLayer, 
    'ICMPv6 Time Exceeded': generalLayer, 
    'Ethernet': generalLayer, 
    'DNS': dnsLayer, 
    'BOOTP': bootpLayer, 
    'DHCP options': dhcpOptionLayer, 
    'IP': generalLayer, 
    'IPv6' : generalLayer, 
    'ICMPv6 Neighbor Discovery Option - Source Link-Layer Address': icmpv6NDOSLLALayer, 
    'SNMP': snmpLayer, 
    'ICMPv6 Neighbor Discovery - Neighbor Solicitation': icmpv6NDNLayer, 
    'ISAKMP SA': isakmpSALayer, 
    'ISAKMP': generalLayer, 
    'Authenticator': generalLayer, 
    'ICMPv6 Destination Unreachable': generalLayer, 
    'ISAKMP Vendor ID': generalLayer, 
    'IPv6 in ICMPv6': generalLayer, 
    'Padding': generalLayer, 
    'UDP': generalLayer, 
    'ICMPv6 Echo Request': generalLayer, 
    'ICMPv6 Parameter Problem': generalLayer, 
    'UDP in ICMP': generalLayer, 
    'TCP': generalLayer
}

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x

class GeneralPacket:

    def __init__(self, packet_id, path):
        self.id = '_'.join(i[:3] for i in packet_id.split('_'))
        self.count = 0
        self.run = False
        self.path = os.path.join(path, self.id) + '.csv'
        self.buffer = []

    
    def getData(self, pkt, label):

        data = {}
        data['label'] = label
        data['time'] = float(pkt.time)
        
        for i, layer in enumerate(expand(pkt), 0):
            try:
                data.update(all_layers[layer.name](layer))
            except:
                data.update(generalLayer(layer))
        self.count += 1
        self.buffer.append(data)
        if self.count % 100 == 0:
            self.write()

    def write(self):
        if not self.run:
            pd.DataFrame(self.buffer).to_csv(self.path, index = False)
            self.run = True
        else:
            pd.DataFrame(self.buffer).to_csv(self.path, header = None, mode = "a", index = False)
        self.buffer = []



def scan_for_unique_packets(fs):

    global cnt
    global start_time, end_time

    pids_ipv4 = set()
    pids_ipv6 = set()
    res_ipv4 = []
    res_ipv6 = []

    for f in fs:

        label = int("201902011450.pcap" not in f)
        try:
            s = PcapReader(f)
            while True:
                try:
                    p = s.read_packet()
                except EOFError:
                    break
                else:
                    cnt = cnt + 1
                    if cnt % 10000 == 0:
                        end_time = time.time()
                        print('progress', cnt / 10000, 'time', end_time - start_time)
                        start_time = time.time()
                        
                    pid = '_'.join([layer.name for i, layer in enumerate(expand(p), 0)])
                    if p.type == 2048:

                        if pid not in pids_ipv4:
                            pids_ipv4.add(pid)
                            data = {}    
                            data['label'] = label
                            data['time'] = float(p.time)
                            for i, layer in enumerate(expand(p), 0):
                                data.update(rename_key(layer.fields, layer.name))
                            res_ipv4.append(data)  
                    else:
                        if pid not in pids_ipv6:
                            pids_ipv6.add(pid)
                            data = {}    
                            data['label'] = label
                            data['time'] = float(p.time)
                            for i, layer in enumerate(expand(p), 0):
                                data.update(rename_key(layer.fields, layer.name))
                            res_ipv6.append(data)                        

            s.close()
            print(f)

        except:
            print('error', f)

    return res_ipv4, res_ipv6


def processFile(f, ppus):

    label = int("201902011450.pcap" not in f)

    try:
        s = PcapReader(f)
        while True:
            try:
                p = s.read_packet()
                packet_id = getPID([layer.name for i, layer in enumerate(expand(p), 0)])
                ppus[packet_id].getData(p, label)
            except EOFError:
                break
            except:
                print('Pkt Process Error')
                p.show()
                print('-----------------')
        s.close()

    except Exception as e:
        print(e)
        print('Error', f)


def generate(path):
    fs = os.listdir(path)
    fs = [os.path.join(path, f) for f in fs]

    example = 'demo/example.pcap'
    pkts = rdpcap(example)
    ppus = [getPIDFromPkt(p) for p in pkts]
    ppus = [(pid, GeneralPacket(pid, 'demo/tables')) for pid in ppus]
    ppus = dict(ppus)

    start_time = time.time()

    for f in fs:
        # if "201902011450" in f:
        #     continue
        try:
            processFile(f, ppus)
        except:
            pass

    # fs = [f for f in fs if "201902011450" not in f]
    # Parallel(n_jobs=6, require='sharedmem')(delayed(processFile)(f, ppus) for f in fs)
        

    end_time = time.time()

    print('Time', end_time - start_time)
    
    # processFile(example, ppus)
    
    [ppu.write() for i, ppu in ppus.items()]

            
def split_pcap(f):

    count = 0
    buffer = []

    try:
        s = PcapReader(f)
        while True:
            try:
                p = s.read_packet()
            except EOFError:
                break
            else:
                buffer.append(p)
                count = count + 1
                if count % 10000 == 0:
                    name,suffix = f.split('.')
                    f_name = name + '_' + str(count / 10000) + '.' + suffix
                    if os._exists(f_name):
                        pass
                    else:
                        writer = PcapWriter(f_name)
                        for p in buffer:
                            writer.write(p)
                        writer.flush()
                        writer.close()
                    buffer = []
        if (len(buffer) != 0):   
            name,suffix = f.split('.')
            writer = PcapWriter(name + '_last.' + suffix)
            for p in buffer:
                writer.write(p)
            writer.flush()
            writer.close()

        s.close()
    except:
        print(f)


@log_time
def build_examples(path: str, filename: str) :

    fs = os.listdir(path)
    fs = [os.path.join(path, f) for f in fs]

    layer_names = set()
    packet_ids = set()
    writer = PcapWriter(filename)

    for f in fs:
        try:
            s = PcapReader(f)
            while True:
                try:
                    p = s.read_packet()
                    layer_name = [layer.name for i, layer in enumerate(expand(p), 0)]
                    layer_names.update(layer_name)
                    packet_id = '_'.join(layer_name)
                    if packet_id not in packet_ids:
                        writer.write(p)
                        packet_ids.add(packet_id)
                except EOFError:
                    print('Finish', f)
                    break
            s.close()
            writer.flush()

        except:
            print('Error', f)
    print(layer_names)
    writer.flush()  
    writer.close()



if __name__ == "__main__":

    path = 'D:\\Code\\Projects\\Data\\ws'
    # build_examples(path, 'example.pcap')
    generate(path)
