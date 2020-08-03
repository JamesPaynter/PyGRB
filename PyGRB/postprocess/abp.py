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
            self.plot_dict['font_size'] = 9
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
