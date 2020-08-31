import numpy as np
import matplotlib.pyplot as plt

from PyGRB.preprocess.BATSE.counts.ttebfits import TimeTaggedRates

GRB = TimeTaggedRates(3770)
bg = GRB._get_rough_backgrounds() * 0.005
times_A = GRB.bin_left[(GRB.bin_left > -0.1) & (GRB.bin_left < 0.15)]
counts_A = GRB.rates[  (GRB.bin_left > -0.1) & (GRB.bin_left < 0.15)] * 0.005

times_B = GRB.bin_left[(GRB.bin_left > 0.3) & (GRB.bin_left < 0.55)]
counts_B = GRB.rates[  (GRB.bin_left > 0.3) & (GRB.bin_left < 0.55)] * 0.005

times_S = GRB.bin_left[(GRB.bin_left > -0.1) & (GRB.bin_left < 0.55)]
counts_S = GRB.rates[  (GRB.bin_left > -0.1) & (GRB.bin_left < 0.55)] * 0.005

for i, c in enumerate(['r', 'orange', 'g', 'b']):
    plt.step(times_A, counts_A[:,i], c = c)
    plt.step(times_B, counts_B[:,i], c = c)

def counts_AA(i):
    return np.sum(counts_A[:,i] - bg[i])

def counts_BB(i):
    return np.sum(counts_B[:,i] - bg[i])

def counts_SS(i):
    return np.sum(counts_S[:,i] - bg[i])

hard_A = counts_AA(2) / counts_AA(1)
hard_B = counts_BB(2) / counts_BB(1)
hard_S = counts_SS(2) / counts_SS(1)
hard_A_err = np.sqrt(1/counts_AA(2)+1/counts_AA(1)) * hard_A
hard_B_err = np.sqrt(1/counts_BB(2)+1/counts_BB(1)) * hard_B
hard_S_err = np.sqrt(1/counts_SS(2)+1/counts_SS(1)) * hard_S
f_A = f'The hardness of pulse A is {hard_A} $\pm$ {hard_A_err}'
f_B = f'The hardness of pulse B is {hard_B} $\pm$ {hard_B_err}'
f_S = f'The hardness of pulse S is {hard_S} $\pm$ {hard_S_err}'
print(f_A)
print(f_B)
print(f_S)




hard_A = np.sum(counts_A[:,2:4] - bg[2:4]) / np.sum(counts_A[:,0:2] - bg[0:2])
hard_B = np.sum(counts_B[:,2:4] - bg[2:4]) / np.sum(counts_B[:,0:2] - bg[0:2])
print(hard_A, hard_B)



# plt.show()


def drn_table():
    duration_table = 'extra/duration_table_5b.txt'
    with open(duration_table) as file:
        lines = file.readlines()


    drn_arr = np.zeros((10000,24))
    #  0 trigger number
    #  1 T50
    #  2 T50 err
    #  3 T50 start
    #  4 T90
    #  5 T90 err
    #  6 T90 start
    #  7 fluence in channel 1
    #  8 fluence in channel 1 error
    #  9 fluence in channel 2
    # 10 fluence in channel 2 error
    # 11 fluence in channel 3
    # 12 fluence in channel 3 error
    # 13 fluence in channel 4
    # 14 fluence in channel 4 error
    # 15 peak flux in 64ms timescale
    # 16 peak flux in 64ms timescale error
    # 17 peak flux in 64ms time
    # 18 peak flux in 256ms timescale
    # 19 peak flux in 256ms timescale error
    # 20 peak flux in 256ms time
    # 21 peak flux in 1024ms timescale
    # 22 peak flux in 1024ms timescale error
    # 23 peak flux in 1024ms time

    for line in lines:
        line = line.strip()
        words = line.split(' ')

        data = []
        for word in words:
            if len(word) > 0:
                data.append(word)
        drn_arr[int(data[0]),:7] = np.array(data).astype('float')




    fluence_tables = ['extra/flux_table_4b.txt', 'extra/flux_table_5b.txt']
    flu_arr = np.zeros((10000,18))
    for table in fluence_tables:
        with open(table) as file:
            lines = file.readlines()
        length = len(lines)
        idx = [5*i for i in range(int(length/5)-1)]
        # np.arange(length,5).astype('int')
        for i in idx:
            [line] = [''.join(lines[i:i+5])]
            line = line.strip()
            words = line.split(' ')
            data = []
            for word in words:
                if len(word) > 0:
                    data.append(word.strip())
            drn_arr[int(data[0]),7:] = np.array(data[1:]).astype('float')
            drn_arr[int(data[0]),0]  = np.array(data[0]).astype('float')



    L = drn_arr[:,0][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0)]
    x = drn_arr[:,4][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0)]
    # x_err = drn_arr[:,5][(drn_arr[:,13]>0) & (drn_arr[:,11]>0) & (drn_arr[:,4]>0)]
    y = (   drn_arr[:,11][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0)]
        /   drn_arr[:,9][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0)]
        )


    from sklearn import mixture
    X = np.vstack([np.log10(x),np.log10(y)]).T
    gmm = mixture.GaussianMixture(n_components=2, covariance_type='full').fit(X)
    Y_ = gmm.predict(X)

    xx = np.linspace(np.min(np.log10(x)),np.max(np.log10(x)), 1000)
    yy = np.linspace(np.min(np.log10(y)),np.max(np.log10(y)), 1000)
    XX, YY = np.meshgrid(xx, yy)
    XY = np.array([XX.ravel(), YY.ravel()]).T
    Z = -gmm.score_samples(XY)
    Z = Z.reshape(XX.shape)
    fig, ax = plt.subplots()
    CS = ax.contour(XX, YY, Z, levels=np.logspace(0, 1, 15), colors = 'k', alpha = 0.6, linewidths = 0.6)
    ax.axvline(np.log10(2), c= 'k', linestyle = '--', linewidth = 0.6)
    ax.scatter(X[Y_ == 0, 0], X[Y_ == 0, 1], marker = '.', color = 'tab:red', s = 3)
    ax.scatter(X[Y_ == 1, 0], X[Y_ == 1, 1], marker = '.', color = 'tab:purple', s = 3)
    # for i, txt in enumerate(L):
    #     ax.annotate(int(txt), (np.log10(x[i]), np.log10(y[i])), fontsize = 6)
    # ax.scatter(X[Y_ == 2, 0], X[Y_ == 2, 1], marker = '.', color = 'tab:green', s = 3)
    ax.scatter(gmm.means_[:,0], gmm.means_[:,1], marker = 'x', color = 'k')
    # ax.errorbar(np.log10(x), np.log10(y), xerr = np.log10(x_err), fmt = ".",
    #             marker = '.', color = 'k', markersize = 0, elinewidth = 0.2)
    x_3770, y_3770 = drn_arr[3770,4], drn_arr[3770,11] / drn_arr[3770,9]
    ax.scatter(np.log10(x_3770), np.log10(y_3770), marker = 'x', color = 'tab:blue', s = 100)
    ax.scatter(np.log10(0.2), np.log10(y_3770), marker = 'x', color = 'g', s = 100)
    ax.set_xlabel('log10 Duration (s) (T90)')
    ax.set_ylabel('log10 Hardness\n (100-300keV fluence / 50-100 keV fluence)')

drn_table()
xxx = [np.log10(0.25), np.log10(0.25), np.log10(0.65)]
yyy = [np.log10(hard_A), np.log10(hard_B), np.log10(hard_S)]
yerr= [np.log10(hard_A_err), np.log10(hard_B_err), np.log10(hard_S_err)]
yerr = np.log10(0.8)
print(yerr)
plt.scatter(xxx[0], yyy[0], color = 'r', marker = 'o', label = 'GRB 950830 Pulse A')
plt.scatter(xxx[1], yyy[1], color = 'r', marker = '+', label = 'GRB 950830 Pulse B')
plt.scatter(xxx[2], yyy[2], color = 'k', marker = 'o', label = 'GRB 950830')
plt.errorbar(xxx,yyy, yerr = yerr, ls='none')
plt.legend()
plt.show()
