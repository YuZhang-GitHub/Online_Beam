clear

%%

num_of_ant = 8;

u = load('user_target_4600.mat');
i1 = load('user_interf_3670.mat');
i2 = load('user_interf_2952.mat');

f = (1/sqrt(32))*exp(1j*angle(u.user_t));
g1 = (1/sqrt(32))*exp(1j*angle(i1.user_i));
g2 = (1/sqrt(32))*exp(1j*angle(i2.user_i_2));

%%

plot_pattern(f(1:num_of_ant, :))
hold on
plot_pattern(g1(1:num_of_ant, :))
hold on
plot_pattern(g2(1:num_of_ant, :))

