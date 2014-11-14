function [data, net] = splitDataAndNet(data, net, ind)
 data = data(:,ind);
 net.std = net.std(ind);
 net.mean = net.mean(ind);
 