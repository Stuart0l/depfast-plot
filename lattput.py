import csv
import matplotlib.pyplot as plt
import numpy as np
import os

home = '/home/xuhao/depfast-prep/'
protocols = ['raft', 'copilot']
rep=[3]

proto_set = {
	'raft': ['raft', 'etcd'],
	'copilot': ['copilot', 'copilot.ref']
}

real_name = {
	'copilot': 'DepFast-Copilot',
	'copilot.ref': 'Copilot',
	'raft': 'DepFast-Raft',
	'etcd': 'etcd',
	'etcd.one': 'etcd (1-core)'
}

marker = {
	'copilot': '-x',
	'copilot.ref': '-^',
	'raft': '-x',
	'etcd': '-^',
	'etcd.one': '-v'
}

annotate = {
	'copilot': 11,
	'raft': 9
}

trail = {
	'copilot': 3,
	'copilot.ref': 5,
	'raft': 3,
	'etcd': 3,
	'etcd.one': 1
}

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
			if proto == 'copilot.ref':
				sample_lat.append(float(line[3])/1000)
			elif proto == 'etcd' or proto == 'etcd.one':
				sample_lat.append(float(line[3])*1000)
			else:
				sample_lat.append(float(line[3]))
			if l%trail[proto] == 0:
				lat.append(np.median(sample_lat))
				tput.append(np.median(sample_tput))
				sample_lat.clear()
				sample_tput.clear()
			l += 1
	
	return lat, tput


def plot_lattput(proto, rep, ax, plt_id):
	for p in proto_set[proto]:
		for r in rep:
			lat, tput = getdata(p, r)

			ax.plot(tput, lat, marker[p], label='{} {}-rep'.format(real_name[p], r),
					linewidth=3, ms=6 if p == 'etcd' else 8, markeredgewidth=3)
			try:

				x = tput[annotate[p]]
				y = lat[annotate[p]]
				# ax.annotate('',
				# 			xy=(x, y),
				# 			xytext=(x+400, y-0.5),
				# 			arrowprops={
				# 				'arrowstyle': 'simple',
				# 				'lw': 3
				# 			})
				ax.plot(x, y, 'r*', label='_nolegend_', ms=12, markeredgewidth=3)
			except:
				pass

	ax.set_xlabel('Throughput (op/s)')
	ax.set_ylabel('Med latency (ms)')
	ax.set_xlim(0)
	ax.set_ylim(0)

	ax.legend(frameon=False, fontsize='small')
	ax.set_box_aspect(0.6)
	ax.set_title('{} Latency-Throughput'.format(plt_id), y=-0.45, fontsize=18, fontweight='bold')


if __name__ == '__main__':
	fig, ax = plt.subplots()
	plot_lattput('copilot.ref', ax, '')

	fig.savefig('lattput.png')