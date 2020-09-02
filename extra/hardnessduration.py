import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc

from PyGRB.preprocess.BATSE.counts.ttebfits import TimeTaggedRates

fig, ax = plt.subplots(nrows = 1)
T90s = np.zeros(8122)
H32s = np.zeros(8122)
bursts = np.array([105,107,108])
# for i in bursts:
# for i in range(105, 8122):
#     try:
#         GRB = TimeTaggedRates(i, times = 'T90')
#         if not np.isnan(GRB.t90):
#             T90s[i] = GRB.t90
#             t = GRB.bin_left
#             s = GRB.t_start
#             bg = GRB._get_rough_backgrounds()
#             r2 = GRB.rates[:,1] - bg[1]
#             r3 = GRB.rates[:,2] - bg[2]
#             H2 = np.sum(r2[(t > s) & (t < (s + GRB.t90))])
#             H3 = np.sum(r3[(t > s) & (t < (s + GRB.t90))])
#             # print('t' = t)
#             print('i = ', i)
#             # print('start =', s)
#             # print('T90 =', s + GRB.t90)
#             # print('H2 = ', H2)
#             # print('H3 = ', H3)
#             # print('\n\n')
#             H32s[i] = H3 / H2
#     except:
#         pass

# mT = np.ma.masked_where(T90s==0, T90s)
# mH = np.ma.masked_where(T90s==0, H32s)
# masked_T90 = np.ma.compressed(mT)
# masked_H32 = np.ma.compressed(mH)

# with open('masked_T90.txt', 'w') as f:
#     for item in masked_T90:
#         f.write("%s\n" % item)
# with open('masked_H32.txt', 'w') as f:
#     for item in masked_H32:
#         f.write("%s\n" % item)
with open('masked_T90.txt', 'r') as f1:
    masked_T90_l = np.array(f1.read().split('\n'))
with open('masked_H32.txt', 'r') as f2:
    masked_H32_l = np.array(f2.read().split('\n'))
masked_T90 = np.zeros(len(masked_T90_l))
masked_H32 = np.zeros(len(masked_H32_l))
for i in range(len(masked_H32_l)):
    try:
        masked_T90[i] = float(masked_T90_l[i])
        masked_H32[i] = float(masked_H32_l[i])
    except:
        pass

mT = np.ma.masked_where(masked_H32<=0, masked_T90)
mH = np.ma.masked_where(masked_H32<=0, masked_H32)
masked_T90 = np.ma.compressed(mT)
masked_H32 = np.ma.compressed(mH)

# plt.scatter(np.arange(len(masked_H32)), masked_H32, marker = '.')
# plt.show()
# H32 = np.ma.masked_where(T90s>0, H32s) #H32s[T90s>0]
 # & (drn_arr[:,0]<300)
ax.scatter(masked_T90, masked_H32, color = 'green', marker = 'x', s = 3)
ax.set_xlabel('T90')
ax.set_ylabel('H32')
ax.set_xscale('log')
ax.set_yscale('log')

# ox.scatter(np.arange(len(masked_T90)), masked_T90)

print('T90 = ', masked_T90)
print('H32 = ', masked_H32)


def get3770(xa):
    GRB = TimeTaggedRates(3770)
    bg = GRB._get_rough_backgrounds() * 0.005

    start_A, end_A = -0.06, 0.1
    start_B, end_B = 0.35, 0.48

    times_A = GRB.bin_left[(GRB.bin_left > start_A) & (GRB.bin_left < end_A)]
    counts_A = GRB.rates[  (GRB.bin_left > start_A) & (GRB.bin_left < end_A)] * 0.005

    times_B = GRB.bin_left[(GRB.bin_left > start_B) & (GRB.bin_left < end_B)]
    counts_B = GRB.rates[  (GRB.bin_left > start_B) & (GRB.bin_left < end_B)] * 0.005

    times_S = GRB.bin_left[(GRB.bin_left > start_A) & (GRB.bin_left < end_B)]
    counts_S = GRB.rates[  (GRB.bin_left > start_A) & (GRB.bin_left < end_B)] * 0.005

    drn_A = times_A[-1] - times_A[0]
    drn_B = times_B[-1] - times_B[0]
    drn_S = times_S[-1] - times_S[0]
    print(drn_A, drn_B)

    o = np.array([-6e3, -1e3, 8e3, 7e3]) * 0.005
    t = GRB.bin_left[(GRB.bin_left > -0.2) & (GRB.bin_left < 0.8)]
    r = GRB.rates   [(GRB.bin_left > -0.2) & (GRB.bin_left < 0.8)] * 0.005
    q = ['lightcoral', 'navajowhite', 'mediumseagreen', 'cornflowerblue']

    # figa, xa = plt.subplots(nrows = 1)
    #
    # xa.axvline(times_A[0], color = 'k', linestyle = ':')
    # xa.axvline(times_B[0], color = 'k', linestyle = ':')
    # xa.axvline(times_A[-1], color = 'k', linestyle = ':')
    # xa.axvline(times_B[-1], color = 'k', linestyle = ':')
    # for i, c in enumerate(['r', 'orange', 'g', 'b']):
    #     xa.step(t, r[:,i] + o[i], color = q[i])
    #     # plt.step(t, r[:,i] + o[i], c = c, alpha = 0.5)
    #     xa.step(times_A, counts_A[:,i] + o[i], c = c)
    #     xa.step(times_B, counts_B[:,i] + o[i], c = c)
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
    f_A = f'The hardness of pulse A is {hard_A:.2f} +/- {hard_A_err:.2f}'
    f_B = f'The hardness of pulse B is {hard_B:.2f} +/- {hard_B_err:.2f}'
    f_S = f'The hardness of pulse S is {hard_S:.2f} +/- {hard_S_err:.2f}'
    print(f_A)
    print(f_B)
    print(f_S)




    hard_A = np.sum(counts_A[:,2:4] - bg[2:4]) / np.sum(counts_A[:,0:2] - bg[0:2])
    hard_B = np.sum(counts_B[:,2:4] - bg[2:4]) / np.sum(counts_B[:,0:2] - bg[0:2])
    print(hard_A, hard_B)

    xxx = np.array([drn_A, drn_B, drn_S])
    yyy = np.array([hard_A,hard_B,hard_S])
    yerr = np.array([hard_A_err,hard_B_err,hard_S_err])
    xa.scatter(xxx[2], yyy[2],
                color = 'k', marker = 'o', label = 'GRB 950830')
    xa.scatter(xxx[0], yyy[0],
                color = 'r', marker = 'o', label = 'GRB 950830 Pulse A')
    xa.scatter(xxx[1], yyy[1],
                color = 'r', marker = '+', label = 'GRB 950830 Pulse B')
    xa.scatter(xxx, yyy-yerr, marker = '_', color = 'k')
    xa.scatter(xxx, yyy+yerr, marker = '_', color = 'k')
    for i, err in enumerate(yerr):
        plt.plot(   [xxx[i], xxx[i]],
                    [yyy[i] - err, yyy[i] + err], color = 'k')
    xa.legend()
    # plt.show()


def drn_table(ax, ox):
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



    L = drn_arr[:,0][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0) & (drn_arr[:,0]<300)]
    x = drn_arr[:,4][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0) & (drn_arr[:,0]<300)]
    # x_err = drn_arr[:,5][(drn_arr[:,13]>0) & (drn_arr[:,11]>0) & (drn_arr[:,4]>0)]
    y = (   drn_arr[:,11][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0) & (drn_arr[:,0]<300)]
        /   drn_arr[:,9][(drn_arr[:,11]>0) & (drn_arr[:,9]>0) & (drn_arr[:,4]>0) & (drn_arr[:,0]<300)]
        )

    print(x)

    from sklearn import mixture
    X = np.vstack([x,y]).T
    gmm = mixture.GaussianMixture(n_components=2, covariance_type='full').fit(X)
    Y_ = gmm.predict(X)

    xx = np.linspace(np.min(x),np.max(x), 1000)
    yy = np.linspace(np.min(y),np.max(y), 1000)
    XX, YY = np.meshgrid(xx, yy)
    XY = np.array([XX.ravel(), YY.ravel()]).T
    Z = -gmm.score_samples(XY)
    Z = Z.reshape(XX.shape)
    # fig, ax = plt.subplots()
    CS = ax.contour(XX, YY, Z, levels=np.logspace(0, 1, 15), colors = 'k',
                        alpha = 0.6, linewidths = 0.6)
    ax.axvline(2, c= 'k', linestyle = '--', linewidth = 0.6)
    ax.scatter(X[Y_ == 0, 0], X[Y_ == 0, 1], marker = '.', color = 'tab:red', s = 3)
    ax.scatter(X[Y_ == 1, 0], X[Y_ == 1, 1], marker = '.', color = 'tab:purple', s = 3)
    # for i, txt in enumerate(L):
    #     ax.annotate(int(txt), (np.log10(x[i]), np.log10(y[i])), fontsize = 6)
    # ax.scatter(X[Y_ == 2, 0], X[Y_ == 2, 1], marker = '.', color = 'tab:green', s = 3)
    ax.scatter(gmm.means_[:,0], gmm.means_[:,1], marker = 'x', color = 'k')
    # ax.errorbar(np.log10(x), np.log10(y), xerr = np.log10(x_err), fmt = ".",
    #             marker = '.', color = 'k', markersize = 0, elinewidth = 0.2)
    x_3770, y_3770 = drn_arr[3770,4], drn_arr[3770,11] / drn_arr[3770,9]
    ax.scatter(x_3770, y_3770, marker = 'x', color = 'tab:blue', s = 100)
    ax.scatter(0.2, y_3770, marker = 'x', color = 'g', s = 100)
    ax.set_xlabel('log10 Duration (s) (T90)')
    ax.set_ylabel('log10 Hardness\n (100-300keV fluence / 50-100 keV fluence)')
    ox.scatter(np.arange(len(x)) + 0.05, x)

# drn_table(ax, ox)
get3770(ax)
plt.show()

#
# figure, axes = plt.subplots()
# x, y = np.log10(np.array([1,2,3])), np.log10(np.array([4,5,6]))
# yerr = np.log10(np.array([0.1,0.2,0.4]))
# axes.scatter(x, y, color = 'k')
# axes.scatter(x, y-yerr, marker = '_', color = 'k')
# axes.scatter(x, y+yerr, marker = '_', color = 'k')
# for i, err in enumerate(yerr):
#     axes.plot([x[i], x[i]], [y[i] - err, y[i] + err], color = 'k')
# # axes.errorbar(x, y, yerr = yerr)
# plt.show()
