# Online Beam Learning for Interference Nulling in Hardware-Constrained mmWave MIMO Systems
<p align="justify">
  This is the simulation codes related to the following article: Y. Zhang and A. Alkhateeb, "<a href="https://ieeexplore.ieee.org/document/10051931">Online Beam Learning for Interference Nulling in Hardware-Constrained mmWave MIMO Systems</a>," in 2022 56th Asilomar Conference on Signals, Systems, and Computers.
</p>


# Abstract of the Article

<p align="justify">
  Employing large antenna arrays is a key characteristic of millimeter wave (mmWave) and terahertz communication systems. Due to the hardware constraints and the lack of channel knowledge, codebook based beamforming/combining is normally adopted to achieve the desired array gain. Existing codebooks, however, are typically pre-defined and focus only on improving the beamforming gain of their target user, without taking interference into account, which incurs critical performance degradation. In this paper, we propose an efficient deep reinforcement learning approach that learns how to iteratively optimize the beam pattern to null the interference. The proposed solution achieves that while not requiring any explicit channel knowledge of the desired or interfering users and without requiring any coordination with the interferers. Simulation results show that the developed solution is capable of finding a well-shaped beam pattern that significantly suppresses the interference while sacrificing negligible beamforming/combing gain, highlighting a promising solution for dense mmWave/terahertz networks.
</p>

<!---
# How to generate this codebook beam patterns figure?
1. Download all the files of this repository.
2. Run `main.py` in `critic_net_training` directory.
3. After it is finished, there will be a file named `critic_params_trsize_2000_epoch_500_3bit.mat` that will be used in the next step.
4. Run `main.py` in `analog_beam_learning` directory.
5. After it is finished, run `read_beams.py` in the same directory.
6. Copy the generated file, i.e., `ULA_PS_only.mat` to the `td_searching` directory.
7. Run `NFWB_BF_TTD_PS_hybrid_low_complexity_search_algorithm.m` in Matlab, which will generate the figure shown below.

![Figure](https://github.com/YuZhang-GitHub/NFWB_BF/blob/main/N_16.png)
-->

# Simulation Description

<p align="justify">
  In the simulation, we emulate a scenario where an _interference unaware_ beam is suffering from the presence of two interfering users. As shown in the figure below, the black profile indicates the pattern of the interference unaware beam that is adopted by the base station, and the yellow and red profiles show the patterns of the interfering users. The goal of the online beam learning algorithm is to come up with another pattern that can avoid introducing interference, as much as possible, from those two interfering transmitters.
</p>

<!---
![Figure](https://github.com/YuZhang-GitHub/tmp/blob/main/paper_fig_1_more_text.png)
-->
<p align="center">
  <img src="https://github.com/YuZhang-GitHub/Online_Beam/blob/main/paper_fig_1_more_text.png" alt="drawing" width="600"/>
</p>

To generate the figure above, simply run `fig_1_agnostic_beam.m` in the `data` folder.

# Beam Learning Scripts

<p float="left">
  <img src="https://github.com/YuZhang-GitHub/Online_Beam/blob/main/polar_linear.png" width="300" />
  <img src="https://github.com/YuZhang-GitHub/Online_Beam/blob/main/cartesian_decibel.png" width="300" />
</p>






<p align="justify">
  In the paper, we propose a multi-level RIS codebook design solution to reduce the design complexity. As shown in the figure below, the distributed RISs consist of four RISs and we further divide each RIS into two subarrays. The design starts from subarray, then the RIS and finally the four RISs.
</p>

Corresponding to the designed solution, we have four subfolders named "LIS_x" in this repository. Each of the folder corresponds to one RIS, consisting of two subarrays. A two-level learning is based on each folder:
- Step 1 (In folder `S1`): Learning from scratch of one subarray.
- Step 2 (In folder `S2`): Transfer learning of the second subarray by initializing the network parameters with the trained first subarray's.
- Step 3 (In folder `C1`): The second-level learning that combines the learning results of the two subarrays.
  
After that, the final, i.e., the third-level learning is performed:
- Step 4 (In folder `Comb_net`): The third-level learning that combines the learning results of the four RISs.

Note: At each step mentioned above, you just simply run `main.py` file.

If you have any problems with generating the figure, please contact [Yu Zhang](https://www.linkedin.com/in/yu-zhang-391275181/).

# License and Referencing
This code package is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/). If you in any way use this code for research that results in publications, please cite our original article:
> Y. Zhang and A. Alkhateeb, "[Learning Reflection Beamforming Codebooks for Arbitrary RIS and Non-Stationary Channels](https://arxiv.org/abs/2109.14909)," in arXiv preprint arXiv:2109.14909.
 
