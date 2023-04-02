clear
close all
clc

%%

load('./user_target_4600.mat') % user_t
load('./user_interf_3670.mat') % user_i_1
user_i_1 = user_i;
load('./user_interf_2952.mat') % user_i_2

%% read results

fid = fopen('./beams/beams_0_max.txt','r');

fseek(fid,0,'eof');

filepos = ftell(fid);

line = '';

flag = 0;

while filepos > 0
    
    fseek(fid,filepos-1,'bof');
    
    char = fread(fid,1,'*char');
    
    if flag == 0
        flag = 1;
    else
        if char == newline
            break;
        end
    end
    
    line = [char,line];
    
    filepos = filepos - 1;
end

% Close the file
fclose(fid);

splitArray = strsplit(line, ',');

beams = str2double(splitArray);

%%

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
raw_cb = beams; % this is for learned beams
CB = (1/sqrt(num_ant))*exp(1j * raw_cb); % (num_beams, num_ant)

% raw_cb_1 = b1.beams;
raw_cb_1 = angle(user_t.');
CB_1 = (1/sqrt(num_ant))*exp(1j * raw_cb_1);

gain_t_old = abs(conj(CB_1)*user_t)^2;
interf_1_old = abs(conj(CB_1)*user_i_1)^2;
interf_2_old = abs(conj(CB_1)*user_i_2)^2;
fprintf('BF Gain old: %.5f.\nInf 1 Gain old: %.5f.\nRatio 1 old: %.5f dB.\n',...
    gain_t_old, interf_1_old, 10*log10(gain_t_old / interf_1_old))
fprintf('BF Gain old: %.5f.\nInf 2 Gain old: %.5f.\nRatio 2 old: %.5f dB.\n',...
    gain_t_old, interf_2_old, 10*log10(gain_t_old / interf_2_old))

gain_t_new = abs(conj(CB)*user_t)^2;
interf_1_new = abs(conj(CB)*user_i_1)^2;
interf_2_new = abs(conj(CB)*user_i_2)^2;
fprintf('BF Gain new: %.5f.\nInf 1 Gain new: %.5f.\nRatio 1 new: %.5f dB.\n',...
    gain_t_new, interf_1_new, 10*log10(gain_t_new / interf_1_new))
fprintf('BF Gain new: %.5f.\nInf 2 Gain new: %.5f.\nRatio 2 new: %.5f dB.\n',...
    gain_t_new, interf_2_new, 10*log10(gain_t_new / interf_2_new))

%% Plot learned beam, polar

proj_egc_i_1 = ctranspose(F)*egc_vec_i_1; % egc_vec should be a column vector
proj_egc_i_1_ = abs(proj_egc_i_1).^2;
proj_egc_i_2 = ctranspose(F)*egc_vec_i_2; % egc_vec should be a column vector
proj_egc_i_2_ = abs(proj_egc_i_2).^2;
proj_lr = ctranspose(F)*CB.'; % the column of CB.' is the desired beam
proj_lr_ = abs(proj_lr).^2;
proj_lr_1 = ctranspose(F)*CB_1.';
proj_lr_1_ = abs(proj_lr_1).^2;

theta_s_degree = (180 / pi) * theta_s;

figure(1);
p(1) = polarplot(theta_s, proj_egc_i_1_.');
p(1).Color = [0.93,0.69,0.13];
hold on
p(2) = polarplot(theta_s, proj_egc_i_2_.');
p(2).Color = [0.64,0.08,0.18];
hold on
p(3) = polarplot(theta_s, proj_lr_.');
p(3).Color = [0.00,0.45,0.74];
hold on
p(4) = polarplot(theta_s, proj_lr_1_.', 'k');
hold off

figure(2);
p(5) = plot(theta_s_degree, 10*log10(proj_egc_i_1_.'));
p(5).Color = [0.93,0.69,0.13];
p(5).LineWidth = 1.0;
hold on
p(6) = plot(theta_s_degree, 10*log10(proj_egc_i_2_.'));
p(6).Color = [0.64,0.08,0.18];
p(6).LineWidth = 1.0;
hold on
% p(7) = plot(theta_s_degree, 10*log10(proj_lr_1_.'), 'k');
% p(7).LineWidth = 1.5;
% hold off
p(8) = plot(theta_s_degree, 10*log10(proj_lr_.'));
p(8).Color = [0.00,0.45,0.74];
p(8).LineWidth = 1.5;
hold off

% xlim([0, max(theta_s_degree)])
xlim([0, 180])
legend([p(5), p(6), p(8)], 'Interferer 1 Radiation Pattern',...
    'Interferer 2 Radiation Pattern',...
    'Interference-Aware Beam Pattern',...
    'Location', 'southeast', 'FontSize', 10);
%     'Interference-Aware Beam Pattern',...
%     'Interference-Agnostic Beam Pattern',...

xlabel('Angle (Degree)')
ylabel('Gain (dB)')
grid on
box on
hold off
