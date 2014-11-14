function network = RidgeLastLayer(network, inputs, targets, alpha, weights, vinputs, vtargets)
% Ridge Regression on last layer of network
% In ridge regression, the model y = xb + constant
% is fit using 'alpha' as quadratic constraint.
% The constant does not get ridged.

  if nargin < 4 || isempty(alpha)
    alpha = 0.1;
  end
  if ~exist('weights', 'var') || isempty(weights)
    weights = ones(size(inputs,1),1);
  end
  x = run_through_network(network(1:end-1),inputs);
%  meanX = mean(x,1); % center data
  meanX = mean(x .* repmat(weights, [ 1, size(x,2)]),1); % center data  
  x = x - repmat(meanX, [size(x,1), 1]);
  x = cat(2, x,  ones(size(x,1),1));
  xw = x .* repmat(weights, [ 1, size(x,2)]);
  a = diag(alpha*ones(size(x,2),1));
  a(end,end) = 0;
  b = inv(x' * xw + a) * (xw' * targets);
  network{end}.W = b(1:end-1,:)';
  bias = b(end,:);
  network{end}.bias = (bias - meanX*network{end}.W')'; % subtract mean from bias
  
%  [x*b run_through_network(network, inputs), targets]
%  keyboard
  t = x*b;
  trainerr = mean(sqrt(sum( (t-targets).^2, 2)) .* weights);
  validerr = NaN;
  if nargin >=6 && ~isempty(vinputs)
      v = run_through_network(network, vinputs);
      validerr = mean(sqrt(sum( (v-vtargets).^2, 2)));
      disp(sprintf('Regression:    TrainErr = %4.3f, ValidErr = %4.3f', trainerr, validerr));
  end
  disp(sprintf('Regression:    TrainErr = %4.3f', trainerr));
  
