function [network, trainerr, validerr] = backprop(network, X, T, max_iter, ...
                                                  targetCost, validationX, validationTargets, ...
                                                  validErrFun, initialfit, weights)
%BACKPROP Trains a network on a dataset using backpropagation
%
%   network = backprop(network, X, T, max_iter)
%
% The function trains the specified network using backpropagation on
% dataset X with targets T for max_iter iterations. The dataset X is an NxD
% matrix, whereas the targets matrix T has size NxM. The variable network
% is a cell array that may be obtained from the TRAIN_DEEP_NETWORK
% function. The function returns the trained network in network.

% This file is modified from the code found in the Matlab Toolbox for 
% Dimensionality Reduction v0.4b (MTDR), (C) Laurens van der Maaten
% Maastricht University, 2007, which was originally adapted from
% code provided by Ruslan Salakhutdinov and Geoff Hinton
% The MTDR can be obtained from http://www.cs.unimaas.nl/l.vandermaaten
% The original deep nets code is from
% http://www.cs.toronto.edu/~hinton/MatlabForSciencePaper.html
%
% (C) 2008 Ian Fasel,
% The University of Texas at Austin


  [n,m] = size(X);

  % Good to do minibatches, but limit memory
  numunits = 0;
  for i = 1:length(network)
    numunits = numunits + size(network{i}.W,2) + length(network{i}.bias);
  end
  A = network{1}.W(1); B = whos('A'); bytes = B.bytes;
  batch_size = min([1000, floor(500*1024^2/(bytes*numunits))])
  %batch_size = min([100, floor(500*1024^2/(bytes*numunits))])

  if ~exist('max_iter', 'var') || isempty(max_iter)
      max_iter = 100;
  end
  if ~exist('initialfit', 'var') || isempty(initialfit)
      initialfit = 5;
  end
  if ~exist('validErrFun', 'var') || isempty(validErrFun)
      validErrFun = 'linSquaredErr';
  end
  if ~exist('weights', 'var') || isempty(weights)
      weights = ones(n,1);
  end


  % For estimating test error
  tindex = randperm(n);
  tinds = tindex(1:min([batch_size n]));
  
  % Perform the gradient descent procedure
  fprintf(1,['Starting ' num2str(max_iter) ' iterations of backprop.\n']);
  if( initialfit>0 && (strcmp(targetCost,'softMax') || strcmp(targetCost,'linSquaredErr')  ))
    transformedX = run_through_network(network(1:end-1), X);
  end
  for iter=1:max_iter
    % Print progress
    trainerr = getError(network, X(tinds,:), T(tinds,:), weights(tinds), validErrFun);
    if exist('validationX', 'var') && ~isempty(validationX)
      validerr = getError(network, validationX, validationTargets, ones(size(validationX,1),1), validErrFun);
      disp(sprintf('Iteration %3d: TrainErr = %4.3f, ValidErr = %4.3f', iter, trainerr, validerr));
    else
      disp(sprintf('Iteration %3d: TrainErr = %4.3f', iter, trainerr));
    end

    % first, train the top layer for awhile
    if iter <= initialfit && (strcmp(targetCost,'softMax') || strcmp(targetCost,'linSquaredErr')  )
      fprintf(1,'.');
      [network(end)] = doBackprop(transformedX, network(end));
    else
      [network] = doBackprop(X, network);
    end
    save network network
  end

  trainerr = getError(network, X(tinds,:), T(tinds,:), weights(tinds), validErrFun);
  if exist('validationX', 'var') && ~isempty(validationX)
    validerr = getError(network, validationX, validationTargets, ones(size(validationX,1),1), validErrFun);
    disp(sprintf('Final        : TrainErr = %4.3f, ValidErr = %4.3f', trainerr, validerr));
  else
    disp(sprintf('Final        : TrainErr = %4.3f', trainerr));
  end

  function [curnet] = doBackprop(traindata, curnet)
    % Loop over all batches
    no_layers = length(curnet);
    index = randperm(n);
    for batch=1:batch_size:n
      if batch + 2*batch_size - 1 > n
        batchend = n;
      else
        batchend = batch + batch_size - 1;
      end
      % Select current batch
      tmpX = traindata(index(batch:batchend),:);
      tmpT = T(index(batch:batchend),:);
      tmpW = weights(index(batch:batchend),:);
  
      % Convert the weights and store them in the network
      v = [];
      for i=1:length(curnet)
          v = [v; curnet{i}.W(:); curnet{i}.bias(:)];
      end
  
      % Conjugate gradient minimization using 3 linesearches
      v = minimize(v, 'backprop_gradient', 3, curnet, tmpX, tmpT, targetCost, tmpW);
  
      % Deconvert the weights and store them in the network
      ind = 1;
      for i=1:no_layers
          curnet{i}.W    = reshape(v(ind:ind - 1 + numel(curnet{i}.W)),    size(curnet{i}.W));     ind = ind + numel(curnet{i}.W);
          curnet{i}.bias = reshape(v(ind:ind - 1 + numel(curnet{i}.bias)), size(curnet{i}.bias));  ind = ind + numel(curnet{i}.bias);
      end
    end
  end
  
  function validerr = getError(network, vX, vT, vW, validErrFun)
    err = 0;
    result = run_through_network(network, vX);
    if strcmp(validErrFun, 'classification')
      for i = 1:size(vX,1)
        [val, ind] = max(result(i,:));
        if ind ~= find(vT(i,:))
          err = err + vW(i);
        end
      end
    else
      for i = 1:size(vX,1)
        err = err + sqrt(sum( (result(i,:)-vT(i,:)).^2)) * vW(i) ;
      end
    end
    validerr = err ./ sum(vW);
  end

end

