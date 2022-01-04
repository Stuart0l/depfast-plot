import csv
import matplotlib.pyplot as plt
import numpy as np
import os

home = '/home/xuhao/depfast-prep/'
protocols = ['raft', 'copilot']
rep=[3, 5]

def getdata(proto, r):
	lat = []
	tput = []
	with open(os.path.join(home, 'results', proto, 'result0_{}.csv'.format(r)), 'r') as f:
		l = 1
		reader = csv.reader(f)
		sample_lat = []
		sample_tput = []
		for line in reader:
			sample_tput.append(float(line[1]))
			sample_lat.append(float(line[3]))
			if l%3 == 0:
				lat.append(np.median(sample_lat))
				tput.append(np.median(sample_tput))
				sample_lat.clear()
				sample_tput.clear()
			l += 1
	
	return lat, tput


def plot_lattput(proto, ax, plt_id):
	for r in rep:
		lat, tput = getdata(proto, r)

		ax.plot(tput, lat, 'x-', label='{} Nodes'.format(r), linewidth=3, ms=8, markeredgewidth=3)

	ax.set_xlabel('Throughput (op/s)')
	ax.set_ylabel('Med latency (ms)')
	ax.set_xlim(0)

	ax.legend(frameon=False)
	ax.set_box_aspect(0.6)
	ax.set_title('{} Throughput-Latency'.format(plt_id), y=-0.35, fontsize=18, fontweight='bold')
