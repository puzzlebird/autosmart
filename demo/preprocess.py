from scapy.all import *
import os
import pandas as pd
import time
from joblib import Parallel, delayed


def rename_key(d: dict, name: str):
    res = {}

    if 'ISAKMP' in name:
        return res
    if 'SNMP' in name:
        return res
    

    for key, item in d.items():
        if 'src' in key or 'dst' in key:
            fields = item.split('.') if '.' in item else item.split(':')
            for i in range(len(fields)):
                res['_'.join([name, key, str(i)])] = str(fields[i])
        elif 'options' in key:
            pass
        elif 'load' in key or 'data' in key:
            res[name + '_' + 'load'] = hash(item)
        elif ('qd' in key or 'ar' in key) and 'DNS' in name:
            pass
        else:
            res[name + '_' + key] = item
    return res

run_ipv4 = False
run_ipv6 = False

f_ipv4 = []
f_ipv6 = []
c_ipv4 = 0
c_ipv6 = 0
cnt = 0
start_time = 0
end_time = 0

def write_ipv4(df):

    global run_ipv4

    if not run_ipv4:
        df.to_csv("ipv4.csv")
        run_ipv4 = True
    else:
        df.to_csv("ipv4.csv", header = None, mode = "a")

def write_ipv6(df):

    global run_ipv6

    if not run_ipv6:
        df.to_csv("ipv6.csv")
        run_ipv6 = True
    else:
        df.to_csv("ipv6.csv", header = None, mode = "a")


def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x


def do_with_pkt(p, label):
    global f_ipv4, f_ipv6, c_ipv4, c_ipv6

    layers = expand(p)

    data = {}
    data['label'] = label
    data['time'] = float(p.time)

    for i, layer in enumerate(layers):
        data.update(rename_key(layer.fields, layer.name))

    
    if p.type == 2048: # indicates ipv4
        f_ipv4.append(data)
        c_ipv4 = c_ipv4 + 1
    else:
        f_ipv6.append(data)
        c_ipv6 = c_ipv6 + 1
    
    if c_ipv4 > 1000:
        write_ipv4(pd.DataFrame(f_ipv4))
        c_ipv4 = 0
        f_ipv4 = []
    if c_ipv6 > 1000:
        write_ipv6(pd.DataFrame(f_ipv6))
        c_ipv6 = 0
        f_ipv6 = []

    return data


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

def write(path, data):

    f = open(path, 'w')
    f.write(str(data))
    f.close()

def getData(path):

    global f_ipv4, f_ipv6, c_ipv4, c_ipv6
    global cnt
    global start_time, end_time

    fs = os.listdir(path)
    fs = [os.path.join(path, f) for f in fs]

    start_time = time.time()

    res_ipv4, res_ipv6 = scan_for_unique_packets(fs)
    # print(res_ipv4)
    write('ipv6_columns', res_ipv6)
    write_ipv4(pd.DataFrame(res_ipv4))
    
    write_ipv6(pd.DataFrame(res_ipv6))


    cnt = 0
    start_time = time.time()

    for f in fs:

        label = int("201902011450.pcap" not in f)

        # if "201902011450.pcap" in f:
        #     continue

        try:
            s = PcapReader(f)
            while True:
                try:
                    p = s.read_packet()
                except EOFError:
                    break
                else:

                    # p.show()

                    cnt = cnt + 1
                    if cnt % 10000 == 0:
                        end_time = time.time()
                        print('progress', cnt / 10000, 'time', end_time - start_time)
                        start_time = time.time()

                    data = do_with_pkt(p, label)
                    # if c_ipv4 % 100 == 0:
                    #     print('ipv4 ', c_ipv4 % 100)
                    # if c_ipv6 % 10000 == 0 and c_ipv6 > 0:
                    #     print('ipv6 ', c_ipv6 / 10000)


            s.close()

            write_ipv4(pd.DataFrame(f_ipv4))
            c_ipv4 = 0
            f_ipv4 = []
            write_ipv6(pd.DataFrame(f_ipv6))
            c_ipv6 = 0
            f_ipv6 = []

        except:

            print(f)
            

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


def find_protocol(names, f):
    try:
        s = PcapReader(f)
        while True:
            try:
                p = s.read_packet()
            except EOFError:
                break
            else:
                pid = '_'.join([layer.name for i, layer in enumerate(expand(p), 0)])
                for name in names:
                    if name in pid:
                        return p

        s.close()
    except:
        print(f)
    return None
    


def find_protocol_dir(names, path):
    fs = os.listdir(path)
    fs = [os.path.join(path, f) for f in fs]

    
    # res = Parallel(n_jobs=6 ,require='sharedmem')(delayed(find_protocol)(names, f) for f in fs)
    res = [find_protocol(names, f) for f in fs]
    writer = PcapWriter('sample.pcap')
    res = [p for p in res if p != None]
    pids = set()
    for p in res:
        pid = '_'.join([layer.name for i, layer in enumerate(expand(p), 0)])
        if pid not in pids:
            print(pid)
            writer.write(p)
            pids.add(pid)
    writer.flush()
    writer.close()


if __name__ == "__main__":
    
    getData('D:\\Code\\ML\\AutoSmart\\demo\\ws')
    # split_pcap('D:\\Code\\ML\\AutoSmart\\demo\\ws\\201902011450.pcap')
    # pkts = find_protocol_dir(['ISAKMP', 'NTPHeader', 'DNS', 'SNMP'], 'D:\\Code\\ML\\AutoSmart\\demo\\ws')
