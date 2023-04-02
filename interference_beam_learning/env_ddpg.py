import os
import torch
import numpy as np


class envCB:

    def __init__(self, ch, num_ant, num_bits, idx, options):

        self.idx = idx
        self.num_ant = num_ant
        self.num_bits = num_bits
        self.cb_size = 2 ** self.num_bits
        self.codebook = self.codebook_gen()
        self.ch = torch.from_numpy(ch).float().cuda()
        self.state = torch.zeros((1, self.num_ant)).float().cuda()
        self.bf_vec = self.init_bf_vec()
        self.previous_gain = 0
        self.previous_sir = 0
        self.previous_gain_pred = 0
        self.th_step = 0.01
        self.threshold = torch.tensor([0]).float().cuda()
        self.threshold_sir = torch.tensor([0]).float().cuda()
        self.count = 1
        self.record_freq = 10
        self.record_decay_th = 1000
        self.bf_gain_t_ach = torch.tensor([0]).float().cuda()
        self.interf_gain_1_ach = torch.tensor([0]).float().cuda()
        self.interf_gain_2_ach = torch.tensor([0]).float().cuda()
        self.gain_record = [np.array(0)]
        self.N_count = 1
        self.best_bf_vec = self.init_best()
        self.opt_bf_gain()
        self.options = options

    def step(self, input_action):  # input_action: (1, num_ant), rep: phase vector
        self.state = input_action
        reward, bf_gain = self.reward_fn(self.state, 0)
        terminal = 0
        return self.state.clone(), reward, bf_gain, terminal

    def reward_fn(self, ph_vec, flag):
        bf_vec = self.phase2bf(ph_vec)
        bf_gain_t, interf_gain_1, interf_gain_2 = self.sir_calc(bf_vec)
        sir = bf_gain_t / (interf_gain_1 + interf_gain_2)

        # if bf_gain_t > self.previous_gain and sir > self.previous_sir:
        #     reward = np.array([1]).reshape((1, 1))
        #     if bf_gain_t > self.threshold and sir > self.threshold_sir:
        #         self.threshold_modif(self.state, bf_gain_t, sir)
        # else:
        #     reward = np.array([-1]).reshape((1, 1))

        # if bf_gain_t > self.previous_gain and sir > self.previous_sir:
        #     reward = np.array([1]).reshape((1, 1))
        #     if bf_gain_t > self.threshold and sir > self.threshold_sir:
        #         self.threshold_modif(ph_vec, bf_gain_t, sir)
        # else:
        #     reward = np.array([-1]).reshape((1, 1))

        if sir > self.previous_sir:
            reward = np.array([1]).reshape((1, 1))
            if sir > self.threshold_sir:
                self.threshold_modif(ph_vec, bf_gain_t, interf_gain_1, interf_gain_2, sir)
        else:
            # if sir >= self.options['sir_req'] and bf_gain_t > self.previous_gain:
            #     reward = np.array([1]).reshape((1, 1))
            # else:
            reward = np.array([-1]).reshape((1, 1))

        if flag:
            self.previous_gain = bf_gain_t
            self.previous_sir = sir
        return reward, bf_gain_t

    def get_reward(self, input_action):
        inner_state = input_action

        # Quantization Processing
        # self.options['ph_table_rep'].cuda()
        mat_dist = torch.abs(inner_state.reshape(self.num_ant, 1) - self.options['ph_table_rep'])
        action_quant = self.options['ph_table_rep'][range(self.num_ant), torch.argmin(mat_dist, dim=1)].reshape(1, -1)

        reward, bf_gain_t = self.reward_fn(action_quant, 1)
        self.count += 1
        return reward, bf_gain_t, action_quant.clone(), action_quant.clone()

    def threshold_modif(self, ph_vec, bf_gain, int_1, int_2, sir):
        self.bf_gain_t_ach = bf_gain
        self.interf_gain_1_ach = int_1
        self.interf_gain_2_ach = int_2
        self.gain_recording(ph_vec, self.idx)
        # self.threshold += self.th_step
        self.threshold = bf_gain
        self.threshold_sir = sir

    def opt_bf_gain(self):
        ch_r = torch.Tensor.cpu(self.ch.clone()).numpy()[0, :self.num_ant].reshape((1, -1))
        ch_i = torch.Tensor.cpu(self.ch.clone()).numpy()[0, self.num_ant:].reshape((1, -1))
        radius = np.sqrt(np.square(ch_r) + np.square(ch_i))
        gain_opt = np.mean(np.square(np.sum(radius, axis=1)))
        print('EGC bf gain: ', gain_opt)
        # return gain_opt

    def phase2bf(self, ph_vec):
        bf_vec = torch.zeros((1, 2 * self.num_ant)).float().cuda()
        for kk in range(self.num_ant):
            bf_vec[0, 2*kk] = torch.cos(ph_vec[0, kk])
            bf_vec[0, 2*kk+1] = torch.sin(ph_vec[0, kk])
        return bf_vec

    def sir_calc(self, bf_vec):
        bf_r = bf_vec[0, ::2].clone().reshape(1, -1)
        bf_i = bf_vec[0, 1::2].clone().reshape(1, -1)

        ch_t_r = torch.squeeze(self.ch[0, :self.num_ant].clone())
        ch_t_i = torch.squeeze(self.ch[0, self.num_ant:].clone())
        bf_gain_t_1 = torch.matmul(bf_r, torch.t(ch_t_r))
        bf_gain_t_2 = torch.matmul(bf_i, torch.t(ch_t_i))
        bf_gain_t_3 = torch.matmul(bf_r, torch.t(ch_t_i))
        bf_gain_t_4 = torch.matmul(bf_i, torch.t(ch_t_r))

        bf_gain_t_r = (bf_gain_t_1 + bf_gain_t_2) ** 2
        bf_gain_t_i = (bf_gain_t_3 - bf_gain_t_4) ** 2
        bf_gain_pattern_t = bf_gain_t_r + bf_gain_t_i
        bf_gain_t = torch.mean(bf_gain_pattern_t)  # bf gain of the target user

        ch_i_r = torch.squeeze(self.ch[1, :self.num_ant].clone())
        ch_i_i = torch.squeeze(self.ch[1, self.num_ant:].clone())
        bf_gain_i_1 = torch.matmul(bf_r, torch.t(ch_i_r))
        bf_gain_i_2 = torch.matmul(bf_i, torch.t(ch_i_i))
        bf_gain_i_3 = torch.matmul(bf_r, torch.t(ch_i_i))
        bf_gain_i_4 = torch.matmul(bf_i, torch.t(ch_i_r))

        bf_gain_i_r = (bf_gain_i_1 + bf_gain_i_2) ** 2
        bf_gain_i_i = (bf_gain_i_3 - bf_gain_i_4) ** 2
        bf_gain_pattern_i = bf_gain_i_r + bf_gain_i_i
        interf_gain_1 = torch.mean(bf_gain_pattern_i)  # bf gain of the interf user 1

        ch_i_r = torch.squeeze(self.ch[2, :self.num_ant].clone())
        ch_i_i = torch.squeeze(self.ch[2, self.num_ant:].clone())
        bf_gain_i_1 = torch.matmul(bf_r, torch.t(ch_i_r))
        bf_gain_i_2 = torch.matmul(bf_i, torch.t(ch_i_i))
        bf_gain_i_3 = torch.matmul(bf_r, torch.t(ch_i_i))
        bf_gain_i_4 = torch.matmul(bf_i, torch.t(ch_i_r))

        bf_gain_i_r = (bf_gain_i_1 + bf_gain_i_2) ** 2
        bf_gain_i_i = (bf_gain_i_3 - bf_gain_i_4) ** 2
        bf_gain_pattern_i = bf_gain_i_r + bf_gain_i_i
        interf_gain_2 = torch.mean(bf_gain_pattern_i)  # bf gain of the interf user 2

        return bf_gain_t, interf_gain_1, interf_gain_2

    def gain_recording(self, bf_vec, idx):
        new_gain = torch.Tensor.cpu(self.bf_gain_t_ach).detach().numpy().reshape((1, 1))
        bf_print = torch.Tensor.cpu(bf_vec).detach().numpy().reshape(1, -1)
        if new_gain > max(self.gain_record):
            self.gain_record.append(new_gain)
            self.best_bf_vec = torch.Tensor.cpu(bf_vec).detach().numpy().reshape(1, -1)
            if os.path.exists('beams/beams_' + str(idx) + '_max.txt'):
                with open('beams/beams_' + str(idx) + '_max.txt', 'ab') as bm:
                    np.savetxt(bm, new_gain, fmt='%.2f', delimiter='\n')
                with open('beams/beams_' + str(idx) + '_max.txt', 'ab') as bm:
                    np.savetxt(bm, bf_print, fmt='%.5f', delimiter=',')
            else:
                np.savetxt('beams/beams_' + str(idx) + '_max.txt', new_gain, fmt='%.2f', delimiter='\n')
                # with open('beams/beams_' + str(idx) + '_max.txt', 'ab') as bm:
                #     np.savetxt(bm, new_gain, fmt='%.2f', delimiter='\n')
                with open('beams/beams_' + str(idx) + '_max.txt', 'ab') as bm:
                    np.savetxt(bm, bf_print, fmt='%.5f', delimiter=',')

    def codebook_gen(self):
        angles = np.linspace(0, 2 * np.pi, self.cb_size, endpoint=False)
        cb = np.exp(1j * angles)
        codebook = torch.zeros((self.cb_size, 2)) # shape of the codebook
        for ii in range(cb.shape[0]):
            codebook[ii, 0] = torch.tensor(np.real(cb[ii]))
            codebook[ii, 1] = torch.tensor(np.imag(cb[ii]))
        return codebook

    def init_bf_vec(self):
        bf_vec = torch.empty((1, 2 * self.num_ant))
        bf_vec[0, ::2] = torch.tensor([1])
        bf_vec[0, 1::2] = torch.tensor([0])
        bf_vec = bf_vec.float().cuda()
        return bf_vec

    def init_best(self):
        ph_book = np.linspace(-np.pi, np.pi, 2 ** self.num_bits, endpoint=False)
        ph_vec = np.array([[ph_book[np.random.randint(0, len(ph_book))] for ii in range(self.num_ant)]])
        bf_complex = np.exp(1j * ph_vec)
        bf_vec = np.empty((1, 2 * self.num_ant))
        for kk in range(self.num_ant):
            bf_vec[0, 2*kk] = np.real(bf_complex[0, kk])
            bf_vec[0, 2*kk+1] = np.imag(bf_complex[0, kk])
        return bf_vec
