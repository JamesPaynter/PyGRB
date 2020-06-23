import numpy as np
import pandas as pd
from abc import ABCMeta

import bilby
from prettytable import PrettyTable


from PyGRB.backend.makemodels import create_model_from_key

class EvidenceTables(object):
    """
    Defines the :class:`~EvidenceTables` class of the *PyGRB* package.
    This is an abstract class that contains the private methods of the
    :class:`~.PulseFitter` class. These methods predominantly translate fitting
    parameters into labels for file or folder names and vice versa.
    """

    def __init__(self):
        super(EvidenceTables, self).__init__()

    def get_evidence_from_models(self, model_dict, channels = None):
        """
        A method to generate the evidence tables for the given channels
        for the specified models. Returns one table per channel. Creates both
        .txt tables and .tex tables.

        Parameters
        ----------
        model_dict : Dict.
            A dictionary of models to be evaluated, and model evidence tabulated.
            Each model will be a dict {}.
        channels : list.
            A list of integers. The channels to be evaluated.
        """

        if type(channels) is not np.ndarray or not isinstance(channels, list):
            channels = [0, 1, 2, 3]

        keys = model_dict.keys()
        models = [model for key, model in model_dict.items()]

        self._evidence_table_to_latex(
                models = models, channels = channels, keys = keys)
        self._evidence_table_to_txt(
                models = models, channels = channels, keys = keys)

    def _evidence_table_to_txt(self, models, channels, keys):
        """
        Returns the evidence tables as a single .txt file.
        See :meth:`~get_evidence_from_models`.
        """
        self.tlabel = self._get_trigger_label()
        self._get_base_directory()
        directory = self.base_folder
        Z_file = f'{directory}/evidence_table_T{self.trigger}_nlive{self.nSamples}.txt'
        open(Z_file, 'w').close()
        for i in channels:
            # hrules = 1 puts a horizontal line between each table entry
            # which makes the table .rst interpretable
            x = PrettyTable(['Model', 'ln Z', 'error'], hrules = 1)
            x.align['Model'] = "l" # Left align models
            # One space between column edges and contents (default)
            x.padding_width = 1
            for k in range(len(models)):
                if 'name' not in [*models[k]]:
                    models[k]['name'] = keys[k]
                self._setup_labels(models[k])
                result_label = f'{self.fstring}{self.clabels[i]}'
                open_result  = f'{self.outdir}/{result_label}_result.json'
                try:
                    result = bilby.result.read_in_result(filename=open_result)
                    x.add_row([ models[k]['name'],
                                f'{result.log_evidence:.2f}',
                                f'{result.log_evidence_err:.2f}'])
                except:
                    print(f'Could not find {open_result}')

            min_e = np.inf
            for row in x:
                row.border = False
                row.header = False
                e = float(row.get_string(fields=['ln Z']).strip())
                if e < min_e:
                    min_e = e
            bayes_facs = []
            for row in x:
                row.border = False
                row.header = False
                e = float(row.get_string(fields=['ln Z']).strip())
                bayes_facs.append(f'{e - min_e:.2f}')
            x.add_column('ln BF', bayes_facs)
            # indentation should be the same as k loop
            # \n padding makes that table .rst interpretable
            with open(Z_file, 'a') as w:
                w.write(f'Channel {i+1}\n\n')
                w.write(str(x))
                w.write('\n\n\n')

    def _evidence_table_to_latex(self, models, channels, keys):
        """
        Returns the evidence tables as a separate .tex files for each channel.
        See :meth:`~get_evidence_from_models`.
        """
        self.tlabel = self._get_trigger_label()
        self._get_base_directory()
        directory = self.base_folder
        columns = ['Model', 'ln evidence', 'ln error', 'ln BF']
        index = np.arange(len(models))
        for i in channels:
            channel_df = pd.DataFrame(columns=columns, index = index)
            for k in range(len(models)):
                if 'name' not in [*models[k]]:
                    models[k]['name'] = keys[k]
                self._setup_labels(models[k])
                result_label = f'{self.fstring}{self.clabels[i]}'
                open_result  = f'{self.outdir}/{result_label}_result.json'
                try:
                    result = bilby.result.read_in_result(filename=open_result)
                    new_row = { 'Model' : [models[k]['name']],
                                'ln evidence' : [result.log_evidence],
                                'ln error' : [result.log_evidence_err],
                                'ln BF' : [result.log_evidence]
                              }
                except:
                    print(f'Could not find {open_result}')
                    new_row = { 'Model' : [models[k]['name']]}
                df = pd.DataFrame(new_row, index = [k])
                channel_df.update(df)
            base_BF = channel_df['ln evidence'].min()
            for k in range(len(models)):
                channel_df.loc[[k], ['ln BF']] = channel_df.loc[[k], ['ln BF']] - base_BF
            print(channel_df.to_latex(  index=False, float_format="{:0.2f}".format))
            channel_df.to_latex(f'{directory}/BF_table_ch_{i+1}.tex',
                                index=False, float_format="{:0.2f}".format)
