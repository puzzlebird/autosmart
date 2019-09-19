from scapy.all import *
import os
import pandas as pd


def rename_key(d: dict, name: str):
    res = {}
    for key, item in d.items():
        if 'src' in key or 'dst' in key:
            fields = item.split('.') if '.' in item else item.split(':')
            for i in range(len(fields)):
                res['_'.join([name, key, str(i)])] = fields[i]
        elif 'options' not in key:
            res[name + '_' + key] = item
    return res

run_ipv4 = False
run_ipv6 = False

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

def getData(path):

    fs = os.listdir(path)
    fs = [os.path.join(path, f) for f in fs]

    f_ipv4 = []
    f_ipv6 = []
    c_ipv4 = 0
    c_ipv6 = 0


    for f in fs:

        label = int("201902011450.pcap" not in f)

        if "201902011450.pcap" in f:
            continue

        try:
            s = PcapReader(f)
            while True:
                try:
                    p = s.read_packet()
                except EOFError:
                    break
                else:

                    p.show()

                    # def expand(x):
                    #     yield x
                    #     while x.payload:
                    #         x = x.payload
                    #         yield x

                    # layers = expand(p)

                    # data = {}

                    # for i, layer in enumerate(layers):

                    #     print(layer.fields, layer.name)
                    #     data.update(rename_key)

                    
                    data['label'] = label
                    if p.haslayer("Ether"):
                        data.update(rename_key(p[Ether].fields, 'ether'))
                    if p.haslayer("IP"):
                        data.update(rename_key(p[IP].fields, 'ip'))
                    if p.haslayer("IPv6"):
                        data.update(rename_key(p[IPv6].fields, 'ipv6'))
                    if p.haslayer("TCP"):
                        data.update(rename_key(p[TCP].fields, 'tcp'))
                    if hasattr(p, 'load'):
                        data['load'] = hash(p.load)
                    data['time'] = p.time
                    if p.type == 2048: # indicates ipv4
                        f_ipv4.append(data)
                        c_ipv4 = c_ipv4 + 1
                    else:
                        f_ipv6.append(data)
                        c_ipv6 = c_ipv6 + 1
                    
                    if c_ipv4 > 999:
                        write_ipv4(pd.DataFrame(f_ipv4))
                        c_ipv4 = 0
                        f_ipv4 = []
                    if c_ipv6 > 999:
                        write_ipv6(pd.DataFrame(f_ipv6))
                        c_ipv6 = 0
                        f_ipv6 = []
            s.close()

            write_ipv4(pd.DataFrame(f_ipv4))
            c_ipv4 = 0
            f_ipv4 = []
            write_ipv6(pd.DataFrame(f_ipv6))
            c_ipv6 = 0
            f_ipv6 = []

        except:

            print(f)
            


if __name__ == "__main__":
    
    getData('D:\\Code\\Projects\\Data\\ws')