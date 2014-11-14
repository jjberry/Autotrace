clear data wdata

data = randn(1000,2) - 0.5;
% for (i=1:100)
%   theta = i * 2 * pi / 100;
%   [data(i,1), data(i,2)] = pol2cart(theta, 1);
% end

% scale and rotate
rot = [4, 0; 0, 1] * [cos(pi/3) sin(pi/3); -sin(pi/3), cos(pi/3)];
data = data * rot;
plot(data(:,1), data(:,2), 'r+'); hold on
axis([-8 8 -8 8])

% whiten
nnet = [];

[wdata, nnet] = normalizedata(data, nnet, 'pca', .95);
plot(wdata(:,1), wdata(:,2), 'b+'); hold off
axis([-8 8 -8 8])

