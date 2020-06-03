import numpy  as np


import bilby
from bilby.core.likelihood import JointLikelihood as bilbyJointLikelihood

from PyGRB.preprocess import BATSEpreprocess
from PyGRB.preprocess import GRB_class
from PyGRB.backend.admin import Admin
from PyGRB.backend.makepriors import MakePriors
from PyGRB.backend.multipriors import MultiPriors
from PyGRB.backend.rateclass import PoissonRate
from PyGRB.backend.makemodels import make_one_pulse_models
from PyGRB.backend.makemodels import make_two_pulse_models
from PyGRB.postprocess.plot_analysis import PlotPulseFit
from PyGRB.postprocess.plot_gl_posteriors import GravLens
from PyGRB.postprocess.make_evidence_tables import EvidenceTables


class PulseFitter(Admin, EvidenceTables):
    """ Wrapper object for Bayesian analysis. """

    def __init__(self,  trigger, times, datatype,
                        priors_pulse_start, priors_pulse_end,
                        priors_td_lo = None, priors_td_hi = None,
                        satellite           = 'BATSE',
                        ## are your bins the right size in rate function ????
                        sampler             = 'dynesty',
                        nSamples            = 200,
                        save = True,
                        **kwargs):

        super(PulseFitter, self).__init__()

        self.HPC = kwargs.get('HPC', False)
        self.variable = kwargs.get('variable')
        self.kwargs   = kwargs

        self.colours             = ['red', 'orange', 'green', 'blue']
        self.clabels             = ['1', '2', '3', '4']
        self.datatype            = datatype
        self.satellite           = satellite
        self.sampler             = sampler
        self.nSamples            = nSamples
        self.trigger             = trigger
        self.injection_parameters= kwargs.get('injection_parameters')
        # self.sampler_kwargs      = kwargs.get('sampler_kwargs')
        self.save                = save


        self.priors_pulse_start = priors_pulse_start
        self.priors_pulse_end   = priors_pulse_end
        self.priors_td_lo       = priors_td_lo
        self.priors_td_hi       = priors_td_hi

        self.MC_counter          = None
        # intialise dict of models
        self.models = {}
        self.offsets = None
        self.p_type  = kwargs.get('p_type', 'docs')
        self.directory_label  = kwargs.get('directory_label')
        self.overwrite_priors = kwargs.get('overwrite_priors')

        self.test = kwargs.get('test')
        if not self.test:
            if datatype == 'tte_list':
                self.GRB = GRB_class.make_GRB(
                    trigger = self.trigger, datatype = self.datatype, **kwargs)
            else:
                try:
                    (self.start, self.end) = times
                    self.GRB = BATSEpreprocess.make_GRB(
                        burst = self.trigger, times = (self.start, self.end),
                        datatype = self.datatype, bgs = False)
                except:
                    self.GRB = BATSEpreprocess.make_GRB(
                        burst = self.trigger, times = times,
                        datatype = self.datatype, bgs = False)
                    self.start = self.GRB.bin_left[60]
                    self.end   = self.GRB.bin_right[-1]
        else:
            self.GRB = kwargs.get('GRB')


    def _split_array_job_to_4_channels(self, models, indices, channels = None):
        for idx in indices:
            n_channels = len(channels)
            m_index    = idx // n_channels
            channel    = channels[idx % n_channels]
            self.main_1_channel(channel, models[m_index])

    def test_pulse_type(self, indices, channels):
        self.models = make_one_pulse_models()
        models = [model for key, model in self.models.items()]
        self._split_array_job_to_4_channels(models, indices, channels)

    def test_two_pulse_models(self, indices, channels):
        self.models = make_two_pulse_models()
        models = [model for key, model in self.models.items()]
        self._split_array_job_to_4_channels(models, indices, channels)

    def main_multi_channel(self, channels, model):
        self._setup_labels(model)
        self.plot_lc(channels = channels, return_axes = False)
        for i in channels:
            self.main_1_channel(i, model)
        self.get_residuals(channels = channels, model = model)


    def main_1_channel(self, channel, model):
        self._setup_labels(model)

        i           = channel

        dict_update = {**self.model, **self.kwargs}
        prior_shell = MakePriors(
                            priors_pulse_start = self.priors_pulse_start,
                            priors_pulse_end = self.priors_pulse_end,
                            priors_td_lo = self.priors_td_lo,
                            priors_td_hi = self.priors_td_hi,
                            channel = i,
                            **dict_update)
        priors = prior_shell.return_prior_dict()

        if self.overwrite_priors:
            for key in self.overwrite_priors:
                prior_keys = [*priors]
                if key in prior_keys:
                    priors[key] = self.overwrite_priors[key]

        x = self.GRB.bin_left
        y = np.rint(self.GRB.counts[:,i]).astype('uint')
        likelihood = PoissonRate(x, y, i, **self.model)

        result_label = f'{self.fstring}{self.clabels[i]}'
        plot_label   = f'{self.outdir}/{result_label}_corner.pdf'
        self._run_bilby( likelihood, priors, model, [channel],
                        result_label, plot_label)

    def main_joint_multi_channel(self, channels, model):
        self._setup_labels(model)
        likelihoods = []
        dict_update = {**self.model, **self.kwargs}
        prior_shell = MultiPriors(  priors_pulse_start = self.priors_pulse_start,
                                    priors_pulse_end = self.priors_pulse_end,
                                    priors_td_lo = self.priors_td_lo,
                                    priors_td_hi = self.priors_td_hi,
                                    channels = channels,**dict_update)
        priors = prior_shell.return_prior_dict()
        x = self.GRB.bin_left
        for i in channels:
            y = np.rint(self.GRB.counts[:,i]).astype('uint')
            likelihoods.append(PoissonRate(x, y, i, **self.model))
        joint_likelihood = bilbyJointLikelihood(*likelihoods)
        result_label = f'{self.fstring}_all'
        plot_label   = f'{self.outdir}/{result_label}_corner.pdf'
        self._run_bilby( joint_likelihood, priors, model, channels,
                        result_label, plot_label)

    def _run_bilby(self, likelihood, priors, model, channels,
                         result_label, plot_label):
        """ Calls to bilby.run_sampler given a likelihood, priors and model.
            Channels should be passed as a list, even if a single value.
            result_label and plot_label are the names for the resultant plots
            and data.
        """
        result = bilby.run_sampler(likelihood   = likelihood,
                                   priors       = priors,
                                   sampler      = self.sampler,
                                   nlive        = self.nSamples,
                                   outdir       = self.outdir,
                                   label        = result_label,
                                   save         = self.save,
                           injection_parameters = self.injection_parameters)
                           # ,
                                   # **self.sampler_kwargs)
        result.plot_corner(filename = plot_label)
        self.get_residuals(channels = channels, model = model)

    def get_residuals(self, channels, model):
        self._setup_labels(model)
        strings = { 'fstring' : self.fstring,
                    'clabels' : self.clabels,
                    'outdir'  : self.outdir,
                    'HPC'     : self.HPC}
        nDraws = 200
        count_fits      = np.zeros((len(self.GRB.bin_left),4))
        residuals       = np.zeros((len(self.GRB.bin_left),4))
        posterior_lines = np.zeros((len(self.GRB.bin_left),nDraws,4))
        for i in channels:
            prior_shell = MakePriors(
                                priors_pulse_start = self.priors_pulse_start,
                                priors_pulse_end = self.priors_pulse_end,
                                priors_td_lo = self.priors_td_lo,
                                priors_td_hi = self.priors_td_hi,
                                channel      = i,
                                **self.model)
            priors = prior_shell.return_prior_dict()

            x = self.GRB.bin_left
            y = np.rint(self.GRB.counts[:,i]).astype('uint')
            likelihood = PoissonRate(x, y, i, **self.model)

            result_label = f'{self.fstring}{self.clabels[i]}'
            open_result  = f'{self.outdir}/{result_label}_result.json'
            result = bilby.result.read_in_result(filename=open_result)

            c_keys = ['a', 'b', 'c', 'd']
            k      = c_keys[i]
            for j in range(1, self.num_pulses + 1):
                try:
                    key = f'constraint_{j}_{k}'
                    del priors[key]
                except:
                    pass
                try:
                    key = f'constraint_{j}_{k}_res'
                    del priors[key]
                except:
                    pass

            posteriors = dict()
            for parameter in priors:
                posteriors[parameter] = result.posterior[parameter].values
            p_chain_len = len(posteriors[f'background_{k}'])

            posterior_draws = np.zeros((len(x), p_chain_len))
            if model['lens']:
                for jj in range(p_chain_len):
                    p_draw = {}
                    for key in posteriors:
                        p_draw[key] = posteriors[key][jj]
                    posterior_draws[:,jj] = likelihood._sum_rates(x, p_draw,
                                                likelihood.calculate_rate_lens)
                posterior_draws_median = np.median(posterior_draws, axis = 1)

            else:
                for jj in range(p_chain_len):
                    p_draw = {}
                    for key in posteriors:
                        p_draw[key] = posteriors[key][jj]
                    posterior_draws[:,jj] = likelihood._sum_rates(x, p_draw,
                                                likelihood.calculate_rate)
                posterior_draws_median = np.median(posterior_draws, axis = 1)

            count_fits[:,i] = posterior_draws_median
            residuals[:,i] = self.GRB.counts[:,i] - posterior_draws_median

            widths = self.GRB.bin_right - self.GRB.bin_left
            rates_i= self.GRB.counts[:,i] / widths
            rates_fit_i = posterior_draws_median / widths
            rates_err_i = np.sqrt(self.GRB.counts[:,i]) / widths
            strings['widths'] = widths
            strings['p_type'] = self.p_type
            posterior_draws   = posterior_draws / widths[:,None]
            posterior_lines[:,:,i] = posterior_draws[:,
                            np.random.randint(p_chain_len, size = nDraws)]
            PlotPulseFit(   x = self.GRB.bin_left, y = rates_i,
                            y_err = rates_err_i,
                            y_cols = self.GRB.colours[i],
                            y_fit = rates_fit_i,
                            channels = [i],
                            datatype = self.datatype,
                            posterior_draws = posterior_lines[:,:,i],
                            nDraws = nDraws,
                            **strings)
        widths = self.GRB.bin_right - self.GRB.bin_left
        rates  = self.GRB.counts / widths[:,None]
        rates_fit = count_fits   / widths[:,None]
        rates_err = np.sqrt(self.GRB.counts) / widths[:,None]
        if len(channels) > 1:
            PlotPulseFit(   x = self.GRB.bin_left, y = rates, y_err = rates_err,
                            y_cols = self.GRB.colours, y_offsets = self.offsets,
                            y_fit = rates_fit,
                            channels = channels,
                            datatype = self.datatype,
                            posterior_draws = posterior_lines,
                            nDraws = nDraws,
                            residuals = True,
                            **strings)

    def plot_lc(self, channels, return_axes = True):
        fstring = f'{self.satellite}_trigger_{self.trigger}_rates'
        self.tlabel = self._get_trigger_label()
        self._get_base_directory()
        directory = self.base_folder
        strings = { 'fstring' : fstring,
                    'clabels' : self.clabels,
                    'outdir'  : directory,
                    'HPC'     : self.HPC}
        strings['p_type'] = self.p_type
        widths      = self.GRB.bin_right - self.GRB.bin_left
        rates       = self.GRB.counts / widths[:,None]
        rates_err   = np.sqrt(self.GRB.counts) / widths[:,None]
        return PlotPulseFit(x = self.GRB.bin_left,
                            y = rates, y_err = rates_err,
                            y_cols = self.GRB.colours, y_offsets = self.offsets,
                            y_fit = None,
                            channels = channels,
                            datatype = self.datatype,
                            posterior_draws = None,
                            nDraws = None,
                            return_axes = return_axes,
                            **strings)

    def lens_calc(self, model, **kwargs):
        self._setup_labels(model)
        if model['lens']:
                GravLens(   fstring = self.fstring,
                            outdir  = self.outdir,
                            p_type  = self.p_type, **kwargs)

if __name__ == '__main__':
    pass
