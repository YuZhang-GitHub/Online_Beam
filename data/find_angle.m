function [max_pow_dir] = find_angle(ch_vec,F)
%FINA_ANGLE Summary of this function goes here
%   ch_vec: column vector
%   F: columns should be the beamsteering vectors

projection = ctranspose(F)*ch_vec;
proj = abs(projection).^2;
[pks, locs] = findpeaks(proj);
[~, I] = sort(pks, 'descend');
locs_descend = locs(I);
max_pow_dir_idx = locs_descend(1);

theta_s = 0:pi/size(F, 2):pi-1e-6; %exclude pi

max_pow_dir = theta_s(max_pow_dir_idx)*(180/pi);

fprintf('Signal direction: %.5f degree (%d/%d). \n', max_pow_dir, max_pow_dir_idx, size(F, 2))

end

