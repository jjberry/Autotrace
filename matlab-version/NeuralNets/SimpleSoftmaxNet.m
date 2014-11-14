% numdata is the number of steps it is allowed to take
numdata = 12;
% numinputs is the number of beliefs (for 3 objects, each with a belief about Red vs Blue
% and Cube vs Cylinder = 3 * 2 * 2
numinputs = 12;
% numoutputs is the action matrix of [L, C, S, R] where:
L = [ 1 0 0 0];
C = [ 0 1 0 0];
S = [ 0 0 1 0];
R = [ 0 0 0 1];
numoutputs = 4;

% make some various random beliefs for the inputs for training
traininputs = zeros(numdata,numinputs);
traininputs(1:numdata,1) = .5;
traininputs(1:numdata,2) = .5;
traininputs(1:numdata,3) = .5;
traininputs(1:numdata,4) = .5;
traininputs = traininputs + randn(numdata,numinputs)*0.1;

% Set up the intended policy to best find out the features of the world
% srsccrsccrcc
traintargets = zeros(numdata,numoutputs);
traintargets(1:1,:) = S;
traintargets(2:2,:) = R;
traintargets(3:3,:) = S;
traintargets(4:4,:) = C;
traintargets(5:5,:) = C;
traintargets(6:6,:) = R;
traintargets(7:7,:) = S;
traintargets(8:8,:) = C;
traintargets(9:9,:) = C;
traintargets(10:10,:) = R;
traintargets(11:11,:) = C;
traintargets(12:12,:) = C;
traintargets = traintargets*0.98 + 0.01;


network{1}.W = randn(numoutputs,numinputs)*0.1;
network{1}.bias = zeros(numoutputs,1);
network{1}.hidtype = 'exp';

[network, trainerr] = backprop(network, traininputs, traintargets, 100, 'softMax');
run_through_network(network, traininputs,'softMax')
