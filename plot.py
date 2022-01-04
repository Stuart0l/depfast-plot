import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import yaml
import lattput

home = '/home/xuhao/depfast-prep/'
typ = 'leader'

num2exp = {
    0: 'No Slowness',
    1: 'CPU Slowness',
    2: 'CPU Contention',
    # 3: 'Disk Slowness',
    # 4: 'Disk Contention',
    5: 'Network Slowness',
    6: 'memory Contention'
}

exp2num = {
    'No Slowness': 0,
    'CPU Slowness': 1,
    'CPU Contention': 2,
    'Disk Slowness': 3,
    'Disk Contention': 4,
    'Network Slowness': 5,
    'memory Contention': 6
}

metrics = [
    'Throughput (op/s)',
    'Average Latency (ms)',
    'P99 Latency (ms)'
]

reps = [3, 5]
typs = ['follower', 'leader']

def load_process_data(protocol, ty, exp, rep):
    loadname = 'result{}_{}.csv'.format(exp, rep)
    filename = os.path.join(home, 'results', protocol, ty, loadname)
    tput = []
    avg = []
    p99 = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                tput.append(float(row[1]))
                avg.append(float(row[2]))
                p99.append(float(row[4]))
            except:
                continue
    return np.median(tput), np.median(avg), np.median(p99)


def plot_figure(all_data, metric, ax):
    # labels = ['{} Nodes'.format(r) for r in reps]
    labels = typs

    x = np.arange(len(labels))
    width = 0.15

    i = -2
    lines = []
    for n, e in num2exp.items():
        try:
            # slow_res = [all_data[r][e][metric] for r in reps]
            slow_res = [all_data[t][3][e][metric] for t in typs]
            lines.append(ax.bar(x + i*width, slow_res, width, label=e))
            i += 1
        except:
            continue
    
    ax.set_ylabel(metrics[metric])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_box_aspect(0.6)

    return lines

def get_cdf_data(protocol, ty, exp, rep):
    true_name = 'fpga_raft' if protocol == 'raft' else protocol
    filepath = os.path.join(home, 'results', protocol, ty, 'yaml')
    filename = '{}_{}_exp{}_t12_c1_s{}_trail1-tpca_none-{}_12_1_-1.yml'.format(
        protocol, ty, exp, rep, true_name
    )
    with open(os.path.join(filepath, filename), 'r') as f:
        data = yaml.safe_load(f)
        latency = data['PAYMENT']['all_latency']
    
    pct_lat = {}
    for k, v in latency.items():
        try:
            pct = round(float(k))
            if pct > 0:
                pct_lat[pct/100] = v
        except:
            continue
    
    return pct_lat


def plot_cdf(all_cdf, ty, rep, ax):
    for e in num2exp.values():
        pct_lat = all_cdf[ty][rep][e]
        pct = list(pct_lat.keys())
        lat = list(pct_lat.values())
        pct.sort()
        lat.sort()
        ax.plot(lat, pct, linewidth=3)

    ax.set_ylabel('CDF ({} Nodes)'.format(rep))
    ax.set_ylim([0, 1])
    ax.set_xlim([0, 15])
    ax.set_xlabel('Latency (ms)')
    # ax.set_xscale('log')
    ax.set_box_aspect(1.2)


if __name__ == '__main__':
    protocol = 'copilot'
    all_data = {}
    all_cdf = {}
    for t in typs:
        all_data[t] = {}
        all_cdf[t] = {}
        for r in reps:
            all_data[t][r] = {}
            all_cdf[t][r] = {}
            for n, e in num2exp.items():
                try:
                    one_result = load_process_data(protocol, t, n, r)
                    all_data[t][r][e] = one_result
                except:
                    all_data[t][r][e] = (0, 0, 0)
                cdf = get_cdf_data(protocol, t, exp2num[e], r)
                all_cdf[t][r][e] = cdf

    plt.rc('font', size=18)
    fig, axes = plt.subplots(1, 4, figsize=(25,5), gridspec_kw={
        'width_ratios': [4,4,2,2]
    })
    
    lines = plot_figure(all_data, 0, axes[1])
    plot_cdf(all_cdf, 'follower', 3, axes[2])
    plot_cdf(all_cdf, 'leader', 3, axes[3])

    fig.legend(lines, labels=num2exp.values(), loc='upper center', ncol=len(num2exp), frameon=False)
    lattput.plot_lattput(protocol, axes[0])

    plt.subplots_adjust(wspace=0.3)
    
    
    # plt.show()
    fig.savefig(os.path.join(home, 'ATC-22/imgs', 'depfast_{}.pdf'.format(protocol)), bbox_inches='tight')
