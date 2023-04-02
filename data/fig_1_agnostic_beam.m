clear;
close all;

load('./user_target_4600.mat') % user_t
load('./user_interf_3670.mat') % user_i_1
load('./user_interf_2952.mat') % user_i_2
b_agnostic = load('./Best_beams_1.mat'); % interference-agnostic beam

num_ant = 8;

over_sampling_y = 1000;
My = num_ant;
[F,~] = UPA_codebook_generator(1,My,1,1,over_sampling_y,1,.5); %F: (#ant, #sampled_directions)
theta_s = 0:pi/(over_sampling_y*My):pi-1e-6; %exclude pi

%% egc beam of interferer
phases_i_1 = angle(user_i_1);
egc_vec_i_1 = (1/sqrt(num_ant))*exp(1j*phases_i_1); % egc_vec == ch
egc_gain_i_1 = abs(egc_vec_i_1'*user_i_1)^2;

phases_i_2 = angle(user_i_2);
egc_vec_i_2 = (1/sqrt(num_ant))*exp(1j*phases_i_2); % egc_vec == ch
egc_gain_i_2 = abs(egc_vec_i_2'*user_i_2)^2;

%% learned beam

raw_cb_agnostic = b_agnostic.beams;
CB_agnostic = (1/sqrt(num_ant))*exp(1j * raw_cb_agnostic);

gain_t_old = abs(conj(CB_agnostic)*user_t)^2;
interf_1_old = abs(conj(CB_agnostic)*user_i_1)^2;
interf_2_old = abs(conj(CB_agnostic)*user_i_2)^2;
fprintf('BF Gain old: %.5f.\nInf 1 Gain old: %.5f.\nRatio 1 old: %.5f dB.\n',...
    gain_t_old, interf_1_old, 10*log10(gain_t_old / interf_1_old))
fprintf('BF Gain old: %.5f.\nInf 2 Gain old: %.5f.\nRatio 2 old: %.5f dB.\n',...
    gain_t_old, interf_2_old, 10*log10(gain_t_old / interf_2_old))

%% Plot learned beam, polar

proj_egc_i_1 = ctranspose(F)*egc_vec_i_1; % egc_vec should be a column vector
proj_egc_i_1_ = abs(proj_egc_i_1).^2;
proj_egc_i_2 = ctranspose(F)*egc_vec_i_2; % egc_vec should be a column vector
proj_egc_i_2_ = abs(proj_egc_i_2).^2;
proj_lr_1 = ctranspose(F)*CB_agnostic.';
proj_lr_1_ = abs(proj_lr_1).^2;

theta_s_degree = (180 / pi) * theta_s;

figure(1);
p(1) = polarplot(theta_s, proj_egc_i_1_.', 'r');
hold on
p(2) = polarplot(theta_s, proj_egc_i_2_.', 'r');
hold on
p(3) = polarplot(theta_s, proj_lr_1_.', 'k');
hold off

figure(2);
p(4) = plot(theta_s_degree, 10*log10(proj_egc_i_1_.'));
p(4).Color = [0.93,0.69,0.13];
p(4).LineWidth = 1.0;
hold on
p(5) = plot(theta_s_degree, 10*log10(proj_egc_i_2_.'));
p(5).Color = [0.64,0.08,0.18];
p(5).LineWidth = 1.0;
hold on
p(6) = plot(theta_s_degree, 10*log10(proj_lr_1_.'), 'k');
p(6).LineWidth = 1.5;
hold on

%% desired and interfering directions
dir_i1 = find_angle(user_i_1, F);
dir_i2 = find_angle(user_i_2, F);
dir_s = find_angle(user_t, F);

vert_start_end = -120:1:0;

p(7) = plot(ones(size(vert_start_end))*dir_s, vert_start_end, '--b');
p(7).LineWidth = 1.5;
hold on
p(8) = plot(ones(size(vert_start_end))*dir_i1, vert_start_end, '--');
p(8).Color = [0.93,0.69,0.13];
p(8).LineWidth = 1.5;
hold on
p(9) = plot(ones(size(vert_start_end))*dir_i2, vert_start_end, '--');
p(9).Color = [0.64,0.08,0.18];
p(9).LineWidth = 1.5;
hold off

% xlim([0, max(theta_s_degree)])
xlim([0, 180])
legend([p(4), p(5), p(6)], 'Interferer 1 Radiation Pattern',...
    'Interferer 2 Radiation Pattern',...
    'Interference-Agnostic Beam Pattern',...
    'Location', 'southeast', 'FontSize', 10);

xlabel('Angle (Degree)')
ylabel('Gain (dB)')
grid on
box on
hold off
