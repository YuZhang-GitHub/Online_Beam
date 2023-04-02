import os
import random
import torch
import numpy as np
import time
from train_ddpg import train
from DataPrep import dataPrep


if __name__ == '__main__':

    t0 = time.time()

    random.seed(7)
    torch.manual_seed(7)

    options = {
        'gpu_idx': 0,
        'num_ant': 8,
        'num_bits': 3,
        'sir_req': 10 ** 4,
        'pf_print': 100,
        'path_target': './user_target_4600.mat',
        'path_interf_1': './user_interf_3670.mat',
        'path_interf_2': './user_interf_2952.mat',
        'save_freq': 50000,
        'save_record': 100,
    }

    train_opt = {
        'state': 0,
        'best_state': 0,
        'num_iter': 1000,
        'tau': 1e-2,
        'overall_iter': 1,
        'replay_memory': [],
        'replay_memory_size': 8192,
        'minibatch_size': 1024,
        'gamma': 0
    }

    if not os.path.exists('beams/'):
        os.mkdir('beams/')

    if not os.path.exists('pfs/'):
        os.mkdir('pfs/')

    ch_t = dataPrep(options['path_target']).reshape(1, -1)
    ch_t = np.concatenate((ch_t[:, :options['num_ant']],
                           ch_t[:, int(ch_t.shape[1] / 2):int(ch_t.shape[1] / 2) + options['num_ant']]), axis=1)
    ch_i_1 = dataPrep(options['path_interf_1']).reshape(1, -1)
    ch_i_1 = np.concatenate((ch_i_1[:, :options['num_ant']],
                             ch_i_1[:, int(ch_i_1.shape[1] / 2):int(ch_i_1.shape[1] / 2) + options['num_ant']]), axis=1)
    ch_i_2 = dataPrep(options['path_interf_2']).reshape(1, -1)
    ch_i_2 = np.concatenate((ch_i_2[:, :options['num_ant']],
                             ch_i_2[:, int(ch_i_2.shape[1] / 2):int(ch_i_2.shape[1] / 2) + options['num_ant']]), axis=1)
    ch = np.concatenate((ch_t, ch_i_1, ch_i_2), axis=0)

    # Quantization settings
    options['num_ph'] = 2 ** options['num_bits']
    options['multi_step'] = torch.from_numpy(
        np.linspace(int(-(options['num_ph'] - 2) / 2),
                    int(options['num_ph'] / 2),
                    num=options['num_ph'],
                    endpoint=True)).type(dtype=torch.float32).reshape(1, -1)
    options['pi'] = torch.tensor(np.pi)
    options['ph_table'] = (2 * options['pi']) / options['num_ph'] * options['multi_step']
    options['ph_table_rep'] = options['ph_table'].repeat(options['num_ant'], 1)

    for beam_id in range(1):
        train(ch, options, train_opt, beam_id)

    print("Time used: {:.2f} seconds.".format(time.time() - t0))
