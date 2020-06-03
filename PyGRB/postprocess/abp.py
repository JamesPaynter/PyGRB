class AbstractBasePlot(object):
    """ Absracts settings for plots for presentations, papers, etc. """

    def __init__(self, plot_type, nChannels, residuals, diagnostics, HPC):
        super(AbstractBasePlot, self).__init__()

        self.plot_dict = dict()
        self.plot_dict['nChannels']   = nChannels
        self.plot_dict['residuals']   = residuals
        self.plot_dict['diagnostics'] = diagnostics

        if nChannels == 1:
            self.plot_dict['heights'] = [3]
            if residuals:
                self.plot_dict['heights'] += [1]
            if diagnostics:
                self.plot_dict['heights'] += [1, 1]
        else:
            self.plot_dict['heights'] = [5]
            if residuals:
                self.plot_dict['heights'] += [1 for i in range(nChannels)]

        if plot_type == 'presentation':
            self.plot_dict['p_type']    = 'presentation'
            self.plot_dict['width']     = 8
            self.plot_dict['linewidth'] = 1.0
            self.plot_dict['font_size'] = 22
            self.plot_dict['heights']  += [1] # based off font size
            self.plot_dict['n_axes']    = len(self.plot_dict['heights'])
            self.plot_dict['ext']       = 'png'

        elif plot_type == 'docs':
            self.plot_dict['p_type']    = 'docs'
            self.plot_dict['width']     = 4
            self.plot_dict['linewidth'] = 0.6
            self.plot_dict['font_size'] = 14
            self.plot_dict['heights']  += [0.8] # based off font size
            self.plot_dict['n_axes']    = len(self.plot_dict['heights'])
            self.plot_dict['ext']       = 'png'

        elif plot_type == 'paper_one_col':
            self.plot_dict['p_type']    = 'paper_one_col'
            self.plot_dict['width']     = 3.54
            # self.plot_dict['width']     = 3.321
            self.plot_dict['linewidth'] = 0.4
            self.plot_dict['font_size'] = 8
            self.plot_dict['heights']  += [0.6] # based off font size
            self.plot_dict['n_axes']    = len(self.plot_dict['heights'])
            self.plot_dict['ext']       = 'pdf'


        elif plot_type == 'paper_two_col':
            self.plot_dict['p_type']    = 'paper_two_col'
            self.plot_dict['width']     = 7.25
            self.plot_dict['linewidth'] = 0.4
            self.plot_dict['font_size'] = 8
            self.plot_dict['heights']  += [0.6] # based off font size
            self.plot_dict['n_axes']    = len(self.plot_dict['heights'])
            self.plot_dict['ext']       = 'pdf'


        elif plot_type == 'thesis':
            print("Not yet implemented, try 'paper_two_col'.")
            self.plot_dict['ext']       = 'pdf'


        elif plot_type == 'animation':
            print("Not yet implemented, try 'presentation'.")
            self.plot_dict['ext']       = 'png'


        else:
            print('Please specify the purpose of this plot')

        if not HPC:
            from matplotlib import rc
            rc('font', **{'family': 'DejaVu Sans',
            'serif': ['Computer Modern'],'size': self.plot_dict['font_size']})
            rc('text', usetex=True)
            rc('text.latex',
            preamble=r'\usepackage{amsmath}\usepackage{amssymb}\usepackage{amsfonts}')

    @staticmethod
    def _make_PP_plot(axes, difference):
        (osm, osr), (slope, intercept, r) = stats.probplot(difference, dist='norm')
        axes.scatter(osm, osr, s=0.1, c='k', marker='+')
        x_vals = np.array([osm[0], osm[-1]])
        y_vals = intercept + slope * x_vals
        axes.plot(x_vals, y_vals, 'k--', linewidth=0.3)
        # adapted from r source code shown in:
        # https://stats.stackexchange.com/questions/111288/confidence-bands-for-qq-line
        xx = difference
        # x<-b0$resid
        # no nans
        # good<-!is.na(x)
        ord = np.sort(xx)
        # ord<-order(x[good])
        # masked array
        # ord.x<-x[good][ord]
        n = len(xx)
        # n<-length(ord.x)
        # ppoints(m, a) = (1:m - a)/(m + (1-a)-a)
        # 1:m = np.arange(1, m+1), a = 0
        P = np.arange(1, n + 1) / n
        # P<-ppoints(n)
        z = stats.norm.ppf(P)
        # z<-qnorm(P)
        # axes_list[2].scatter(z,x)
        # plot(z,ord.x,type="n")
        # coeffs =
        # extracts coefficients after fitting a robust linear model
        # coef<-coef(rlm(ord.x~z))
        # a<-coef[1]
        # b<-coef[2]
        # abline(a,b,col="red",lwd=2)
        # confidence interval desired
        conf = 0.95
        # conf<-0.95
        zz = stats.norm.ppf(1 - (1 - conf) / 2)
        # zz<-qnorm(1-(1-conf)/2)
        SE = (slope / stats.norm(0, 1).pdf(z)) * np.sqrt(P * (1 - P) / n)
        # SE<-(b/dnorm(z))*sqrt(P*(1-P)/n)     #[WHY?]
        fit = intercept + slope * z
        # fit.value<-a+b*z
        upper = fit + zz * SE
        # upper<-fit.value+zz*SE
        lower = fit - zz * SE
        # lower<-fit.value-zz*SE
        axes.plot(z, upper, 'k:', linewidth=0.3)
        axes.plot(z, lower, 'k:', linewidth=0.3, label='$95\%$ CI')
        axes.legend()

    @staticmethod
    def _make_correlogram(axes, x, difference):
        c, c2 = autocorrelations(difference)
        # https://online.stat.psu.edu/stat510/lesson/2/2.2
        # partial acf does not seem to add much more information
        # from statsmodels.tsa.stattools import acf, pacf
        # lag_acf = acf(difference)
        # lag_pacf = pacf(difference)
        axes.scatter(x[1:], c[1:], s=0.1, c='k', marker='+')
        # axes.scatter(x[1:len(lag_pacf)], lag_pacf[1:],  s = 0.1, c = 'r', marker = 'x')
        # axes.scatter(x, c2, s = 0.1, c = 'r', marker = 'x')
        n = len(x)
        z95 = 1.959963984540054
        z99 = 2.5758293035489004
        axes.axhline(y=z99 / np.sqrt(n), c='k', linestyle=':',
                             linewidth=0.3, label='$99\%$ CI')
        axes.axhline(y=z95 / np.sqrt(n), c='k', linestyle='--',
                             linewidth=0.3, label='$95\%$ CI')
        axes.axhline(y=-z95 / np.sqrt(n), c='k', linestyle='--',
                             linewidth=0.3)
        axes.axhline(y=-z99 / np.sqrt(n), c='k', linestyle=':',
                             linewidth=0.3)
        axes.set_xlabel('time since trigger (s)')
        axes.legend()
