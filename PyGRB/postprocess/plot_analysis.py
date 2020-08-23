import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from PyGRB.postprocess.abp import AbstractBasePlot


def autocorrelations(x):
    """ Do a test to see if they are Gaussian distributed? """
    acf  = np.correlate(x, x, mode='full')[len(x)-1:]
    acf2 = np.correlate(x**2, x**2, mode='full')[len(x)-1:]
    acf, acf2 = acf / np.max(acf), acf2 / np.max(acf2)
    return acf, acf2


class PlotPulseFit(AbstractBasePlot):
    """docstring for PlotPulseFit."""

    def __init__(self, *args, **kwargs):
        plot_type = kwargs.get('p_type', 'presentation')
        residuals = kwargs.get('residuals')
        channels  = kwargs.get('channels')
        datatype  = kwargs.get('datatype')
        diagnostics = kwargs.get('diagnostics')
        HPC = kwargs.get('HPC')

        super(PlotPulseFit, self).__init__( plot_type = plot_type,
                                            nChannels = len(channels),
                                            residuals = residuals,
                                            diagnostics = diagnostics,
                                            HPC = HPC)

        if datatype != 'tte_list':
            if len(channels) > 1:
                self.plot_multi_channel(*args, **kwargs)
            else:
                self.plot_single_channel(*args, **kwargs)
        else:
            if len(channels) > 1:
                self.plot_multi_channel_tte(*args, **kwargs)
            else:
                self.plot_single_channel_tte(*args, **kwargs)

    def _return_plot_kwargs(self, **kwargs):
        posterior_draws  = kwargs.get('posterior_draws')
        nDraws  = kwargs.get('nDraws')
        fstring = kwargs.get('fstring')
        clabels = kwargs.get('clabels')
        outdir  = kwargs.get('outdir')
        widths  = kwargs.get('widths')
        p_type  = kwargs.get('p_type')
        return posterior_draws, nDraws, fstring, clabels, outdir, widths, p_type
        
    def plot_single_channel(self, x, y, y_err, y_cols, y_fit, channels,**plot_kwargs):
        # posterior_draws  = kwargs.get('posterior_draws')
        # nDraws  = kwargs.get('nDraws')
        # fstring = kwargs.get('fstring')
        # clabels = kwargs.get('clabels')
        # outdir  = kwargs.get('outdir')
        # widths  = kwargs.get('widths')
        # p_type  = kwargs.get('p_type')
        posterior_draws, nDraws, fstring, clabels, outdir, widths, p_type = \
            self._return_plot_kwargs(**plot_kwargs)

        # arbitrary scaled height
        height  = (self.plot_dict['width'] / 1.8) * 2
        # constrained_layout = False -> don't mess with my placing
        fig     = plt.figure(   figsize = (self.plot_dict['width'], height),
                                constrained_layout = False)
        # add an extra column on the left for the main axes labels
        spec    = gridspec.GridSpec(ncols=2, nrows = self.plot_dict['n_axes'],
                                    figure=fig,
                                    height_ratios = self.plot_dict['heights'],
                                    width_ratios=[0.05, 0.95],
                                    hspace=0.0, wspace=0.0)
        # axes label on the LHS of plot
        ax = fig.add_subplot(spec[0:2, 0], frameon = False)
        if self.plot_dict['n_axes'] > 3:
            ax2 = fig.add_subplot(spec[2, 0], frameon = False)
            ax3 = fig.add_subplot(spec[3, 0], frameon = False)

        # main plot axes
        fig_ax1 = fig.add_subplot(spec[0, 1])
        # list of residual channel axes to append to
        axes_list = []

        k = [channels]
        fig_ax1.plot(   x, y, c = y_cols,
                        drawstyle='steps-mid',
                        linewidth = self.plot_dict['linewidth'])
        if y_fit is not None:
            fig_ax1.plot(x, y_fit, 'k', linewidth = self.plot_dict['linewidth'])
        if posterior_draws is not None:
            drawLines = []
            for ii in range(nDraws):
                drawLines.append(x)
                drawLines.append(posterior_draws[:,ii])
            d = {'c': 'k', 'linewidth' : 0.5, 'alpha' : 0.02}
            fig_ax1.plot(*drawLines, **d)
        if y_fit is not None:
            fig_ax1.fill_between(x, y + y_err, y - y_err, step = 'mid',
                                color = y_cols, alpha = 0.15)

        ticks = fig_ax1.get_yticks()
        ticks = ticks[1:] if ticks[0] == 0 else ticks
        fig_ax1.set_yticks(ticks)

        for i in range(self.plot_dict['n_axes'] - 2):
            axes_list.append(fig.add_subplot(spec[i+1, 1]))
        if self.plot_dict['residuals']:
            # get the residual
            difference = y - y_fit
            # plot that residual
            axes_list[0].plot(  x, difference, c = y_cols,
                                drawstyle='steps-mid',
                                linewidth = self.plot_dict['linewidth'])



            axes_list[0].fill_between(x, y_err,  - y_err,
                                         step = 'mid', color = y_cols,
                                         alpha = 0.15)
            axes_list[0].axhline(0, c = 'k', linewidth = 0.2)
            axes_list[0].axhline(0, c = 'k', linewidth = 0.5)
        if y_fit is not None:
            fig_ax1.set_ylim(bottom = min(y - y_err), top = max(y + y_err))

        if self.plot_dict['residuals']:
            ticks = axes_list[0].get_yticks()
            ticks = [int(tick) for tick in ticks if tick >= 0]
            ticks = ticks[0:2] if len(ticks) > 2 else ticks
            axes_list[0].set_xlim(x[0], x[-1])
            axes_list[0].set_yticks(ticks)
        fig_ax1.set_xlim(x[0], x[-1])
        ax.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax.set_ylabel('Counts / sec')
        if self.plot_dict['n_axes'] > 3:
            difference = y - y_fit
            PlotPulseFit._make_correlogram(axes_list[1], x, difference)
            PlotPulseFit._make_PP_plot(axes_list[2], difference)
            axes_list[1].set_xlim(x[0], x[-1])
            ax2.tick_params(labelcolor='none', top=False,
                            bottom=False, left=False, right=False)
            ax3.tick_params(labelcolor='none', top=False,
                            bottom=False, left=False, right=False)
            ax2.set_ylabel('Correlogram')
            ax3.set_ylabel('Probability\nPlot')
        plt.subplots_adjust(left=0.16)
        plt.subplots_adjust(right=0.98)
        plt.subplots_adjust(top=0.98)
        plt.subplots_adjust(bottom=0.05)

        if p_type == 'animation':
            plot_name=f'{outdir}/anim/{fstring}{clabels[channels[0]]}_rates.{self.plot_dict["ext"]}'
        else:
            plot_name=f'{outdir}/{fstring}{clabels[channels[0]]}_rates.{self.plot_dict["ext"]}'
        fig.savefig(plot_name, dpi = 200)
        plt.close(fig)



    def plot_multi_channel(self,    x, y, y_err, y_cols, y_offsets, y_fit,
                                    channels, **kwargs):
        fstring = kwargs.get('fstring')
        clabels = kwargs.get('clabels')
        outdir  = kwargs.get('outdir')
        nDraws  = kwargs.get('nDraws')
        posterior_draws  = kwargs.get('posterior_draws')

        # for GUI
        return_axes  = kwargs.get('return_axes')
        height = (self.plot_dict['width'] / 1.8) * 2
        # constrained_layout = False -> don't mess with my placing
        fig = plt.figure(figsize = (self.plot_dict['width'], height),
                                    constrained_layout=False)
        # add an extra column on the left for the main axes labels
        spec = gridspec.GridSpec(   ncols = 2,
                                    nrows = self.plot_dict['n_axes'],
                                    figure = fig,
                                    height_ratios = self.plot_dict['heights'],
                                    width_ratios = [0.05, 0.95],
                                    hspace = 0.0, wspace = 0.0)
        # axes label on the LHS of plot
        ax = fig.add_subplot(spec[:, 0], frameon = False)
        # main plot axes
        fig_ax1 = fig.add_subplot(spec[0, 1])
        # list of residual channel axes to append to
        axes_list = []

        for i, k in enumerate(channels):
            if type(y_offsets) is not np.ndarray:
                y_offsets = np.zeros(4)
            line_label = f'offset {y_offsets[k]:+,}'
            fig_ax1.plot(   x, y[:,k] + y_offsets[k], c = y_cols[k],
                            drawstyle='steps-mid', linewidth = 0.4,
                            label = line_label)
            if y_fit is not None:
                fig_ax1.plot(x, y_fit[:,k] + y_offsets[k], 'k', linewidth = 0.4)
            fig_ax1.fill_between(x, y[:,k] + y_offsets[k] + y_err[:,k],
                                    y[:,k] + y_offsets[k] - y_err[:,k],
                                    step = 'mid', color = y_cols[k],
                                    alpha = 0.15)
            if posterior_draws is not None:
                drawLines = []
                for ii in range(nDraws):
                    drawLines.append(x)
                    drawLines.append(posterior_draws[:,ii,i] + y_offsets[k])
                d = {'c': 'k', 'linewidth' : 0.5, 'alpha' : 0.02}
                fig_ax1.plot(*drawLines, **d)

            # append another axes to the residual list
            if self.plot_dict['residuals']:
                axes_list.append(fig.add_subplot(spec[i+1, 1]))
                # get the residual
                if y_fit is not None:
                    difference = y[:,k] - y_fit[:,k]
                    # plot that residual
                    axes_list[i].fill_between(x, y_err[:,k],
                                                 -y_err[:,k],
                                                 step = 'mid', color = y_cols[k],
                                                 alpha = 0.15)
                    axes_list[i].axhline(0, c = 'k', linewidth = 0.2)
                    axes_list[i].plot(  x, difference, c = y_cols[k],
                                        drawstyle='steps-mid',  linewidth = 0.4)
                    # set the axes limits for the newly plotted axis
                    axes_list[i].set_xlim(x[0], x[-1])
                    # get rid of x ticks
                    if i < len(channels) - 1:
                        axes_list[i].set_xticks(())
                    tick = int(np.max(difference) * 0.67 / 100) * 100
                    axes_list[i].set_yticks(([int(0), tick]))

        if self.plot_dict['residuals']:
            axes_list[-1].set_xlabel('Time since trigger (s)')
        else:
            fig_ax1.set_xlabel('Time since trigger (s)')
        ax.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax.set_ylabel('Counts / sec')
        plt.subplots_adjust(left=0.16)
        plt.subplots_adjust(right=0.98)
        plt.subplots_adjust(top=0.98)
        plt.subplots_adjust(bottom=0.05)

        fig_ax1.ticklabel_format(axis = 'y', style = 'sci')
        if y_offsets.any() > 0:
            fig_ax1.legend()

        fig_ax1.set_xlim(x[0], x[-1])
        if self.plot_dict['p_type'] == 'animation':
            plot_name=f'{outdir}/anim/{fstring}_rates.{self.plot_dict["ext"]}'
        else:
            plot_name=f'{outdir}/{fstring}_rates.{self.plot_dict["ext"]}'
        if not return_axes:
            fig.savefig(plot_name, dpi = 200)
            plt.close(fig)
        else:
            return fig_ax1

    @staticmethod
    def plot_single_channel_tte(x, y, y_cols, y_fit, channels,**strings):
        fstring = strings.get('fstring')
        clabels = strings.get('clabels')
        outdir  = strings.get('outdir')
        widths  = strings.get('widths')
        n_axes  = 1 + 3 +1
        width   = 3.321
        # arbitrary scaled height
        height  = (width / 1.8) * 2
        # ratio of the heights of each of the subpanels
        # 5 for main to 1 per residual seems to work well (for 4 or 1 channel)
        heights = [3, 1, 3, 3] + [0.6]
        # heights = [5] + ([1 for i in range(n_axes - 2)]) + [0.6]
        # constrained_layout = False -> don't mess with my placing
        fig     = plt.figure(figsize = (width, height), constrained_layout=False)
        # add an extra column on the left for the main axes labels
        spec    = gridspec.GridSpec(ncols=2, nrows=n_axes, figure=fig,
                                    height_ratios=heights,
                                    width_ratios=[0.05, 0.95],
                                    hspace=0.0, wspace=0.0)
        # axes label on the LHS of plot
        ax      = fig.add_subplot(spec[0:2, 0], frameon = False)
        ax2     = fig.add_subplot(spec[2, 0], frameon = False)
        ax3     = fig.add_subplot(spec[3, 0], frameon = False)
        # main plot axes
        fig_ax1 = fig.add_subplot(spec[0, 1])
        # list of residual channel axes to append to
        axes_list = []

        k = [channels]
        # fig_ax1.plot(   x, y, c = y_cols,
        #                 drawstyle='steps-mid', linewidth = 0.4)
        fig_ax1.plot(x, y_fit, 'k', linewidth = 0.4)
        # fig_ax1.fill_between(x, y + y_err, y - y_err, step = 'mid',
        #                         color = y_cols, alpha = 0.15)

        ticks = fig_ax1.get_yticks()
        ticks = ticks[1:] if ticks[0] == 0 else ticks
        fig_ax1.set_yticks(ticks)

        for i in range(n_axes - 2):
            axes_list.append(fig.add_subplot(spec[i+1, 1]))
        # get the residual
        difference = y - y_fit
        # plot that residual
        # axes_list[0].plot(  x, difference, c = y_cols,
        #                     drawstyle='steps-mid',  linewidth = 0.4)



        # axes_list[0].fill_between(x, y_err,  - y_err,
        #                              step = 'mid', color = y_cols,
        #                              alpha = 0.15)
        # axes_list[0].axhline(0, c = 'k', linewidth = 0.2)

        # fig_ax1.set_ylim(bottom = min(y - y_err), top = max(y + y_err))


        ticks = axes_list[0].get_yticks()
        ticks = [int(tick) for tick in ticks if tick >= 0]
        ticks = ticks[0:2] if len(ticks) > 2 else ticks
        axes_list[0].set_yticks(ticks)

        # PlotPulseFit._make_correlogram(axes_list[1], x, difference)

        axes_list[0].set_xlim(x[0], x[-1])
        axes_list[1].set_xlim(x[0], x[-1])


        ax.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax2.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax3.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax.set_ylabel('counts / sec')
        ax2.set_ylabel('Correlogram')
        ax3.set_ylabel('Probability Plot')
        plt.subplots_adjust(left=0.16)
        plt.subplots_adjust(right=0.98)
        plt.subplots_adjust(top=0.98)
        plt.subplots_adjust(bottom=0.05)

        # PlotPulseFit._make_PP_plot(axes_list[2], difference)

        fig_ax1.set_xlim(x[0], x[-1])

        plot_name=f'{outdir}/{fstring}_result_{clabels[channels[0]]}_rates.{self.plot_dict["ext"]}'
        fig.savefig(plot_name)
        plt.close(fig)

    @staticmethod
    def plot_multi_channel_tte(x, y, y_err, y_cols, y_offsets, y_fit, channels, **strings):
        fstring = strings.get('fstring')
        clabels = strings.get('clabels')
        outdir  = strings.get('outdir')

        # number axes is the main plot plus one per channel for residuals
        # extra axis for x-label
        n_axes  = len(channels) + 2
        # width of a single column of a journal article
        width   = 3.321
        # arbitrary scaled height
        height  = (width / 1.8) * 2
        # ratio of the heights of each of the subpanels
        # 5 for main to 1 per residual seems to work well (for 4 or 1 channel)
        heights = [5] + ([1 for i in range(n_axes - 2)]) + [0.6]
        # constrained_layout = False -> don't mess with my placing
        fig     = plt.figure(figsize = (width, height), constrained_layout=False)
        # add an extra column on the left for the main axes labels
        spec    = gridspec.GridSpec(ncols=2, nrows=n_axes, figure=fig,
                                    height_ratios=heights,
                                    width_ratios=[0.05, 0.95],
                                    hspace=0.0, wspace=0.0)
        # axes label on the LHS of plot
        ax      = fig.add_subplot(spec[:, 0], frameon = False)
        # main plot axes
        fig_ax1 = fig.add_subplot(spec[0, 1])
        # list of residual channel axes to append to
        axes_list = []

        for i, k in enumerate(channels):
            # adds offsets if there is more than one channel
            if y_offsets:
                line_label = f'offset {y_offsets[k]:+,}'
                # fig_ax1.plot(   x, y[:,k] + y_offsets[k], c = y_cols[k],
                #                 drawstyle='steps-mid', linewidth = 0.4,
                #                 label = line_label)
                fig_ax1.plot(   x, y_fit[:,k] + y_offsets[k],
                                c = y_cols[k], linewidth = 0.4)
                # fig_ax1.fill_between(x, y[:,k] + y_offsets[k] + y_err[:,k],
                #                         y[:,k] + y_offsets[k] - y_err[:,k],
                #                         step = 'mid', color = y_cols[k],
                #                         alpha = 0.15)
            else:
                # fig_ax1.plot(   x, y[:,k], c = y_cols[k],
                #                 drawstyle='steps-mid', linewidth = 0.4)
                fig_ax1.plot(x, y_fit, c = y_cols[k], linewidth = 0.4)
                #, label = plot_legend)
                # fig_ax1.fill_between(x, y[:,k] + y_err[:,k], y[:,k] - y_err[:,k], step = 'mid',
                #                         color = y_cols[k], alpha = 0.15)
            axes_list.append(fig.add_subplot(spec[i+1, 1]))

        axes_list[-1].set_xlabel('Time since trigger (s)')
        ax.tick_params(labelcolor='none', top=False,
                        bottom=False, left=False, right=False)
        ax.set_ylabel('counts / sec')
        plt.subplots_adjust(left=0.16)
        plt.subplots_adjust(right=0.98)
        plt.subplots_adjust(top=0.98)
        plt.subplots_adjust(bottom=0.05)

        fig_ax1.ticklabel_format(axis = 'y', style = 'sci')
        # if y_offsets:
        #     fig_ax1.legend()

        fig_ax1.set_xlim(x[0], x[-1])
        plot_name = f'{outdir}/{fstring}_rates.{self.plot_dict["ext"]}'
        fig.savefig(plot_name)
        plt.close(fig)

    @staticmethod
    def _make_PP_plot(axes, difference):
        (osm, osr), (slope, intercept, r) = stats.probplot(difference, dist='norm')
        axes.scatter(osm, osr, s=0.3, c='k', marker='+')
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
        axes.legend(fontsize = 9)

    @staticmethod
    def _make_correlogram(axes, x, difference):
        c, c2 = autocorrelations(difference)
        # https://online.stat.psu.edu/stat510/lesson/2/2.2
        # partial acf does not seem to add much more information
        # from statsmodels.tsa.stattools import acf, pacf
        # lag_acf = acf(difference)
        # lag_pacf = pacf(difference)
        axes.scatter(x[1:], c[1:], s=0.3, c='k', marker='+')
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
        axes.legend(fontsize = 9)

if __name__ == '__main__':
    pass
