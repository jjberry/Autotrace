function [C, dC] = backprop_gradient(v, network, X, targets, targetCost, weights)
% BACKPROP_GRADIENT Compute the cost and gradient for CG optimization of a neural network
%
%   [C, dC] = backprop_gradient(v, network, X, targets, targetCost)
%
% Compute the value of the cost function, as well as the corresponding 
% gradient for conjugate-gradient optimization of a neural network.

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


  % Initialize some variables
  n = size(X, 1);
  numHiddenLayers = length(network);

  % Deconvert the weights and store them in the network
  ind = 1;
  for i=1:numHiddenLayers
    network{i}.W    = reshape(v(ind:ind - 1 + numel(network{i}.W)),    size(network{i}.W));     ind = ind + numel(network{i}.W);
    network{i}.bias = reshape(v(ind:ind - 1 + numel(network{i}.bias)), size(network{i}.bias));  ind = ind + numel(network{i}.bias);
  end
  
  % Run the data through the network
  acts = cell(1, numHiddenLayers + 1);
  acts{1} = X;
  for i=1:numHiddenLayers
    switch(network{i}.hidtype)
    case 'sigmoid'
      acts{i + 1} = 1 ./ (1 + exp(-(acts{i} * network{i}.W'  + repmat(network{i}.bias', [n 1]))));
    case {'gaussian', 'exp'}
      acts{i + 1} = acts{i} * network{i}.W' + repmat(network{i}.bias', [n 1]);
    otherwise
      error('unknown hidden layer type.')
    end
  end 

  % store gradients for output
  dW = cell(1, numHiddenLayers);
  db = cell(1, numHiddenLayers);

  switch targetCost
  case 'crossEntropy'
    % Compute value of cost function (= cross entropy)
    C = (-1 / n) .* sum(sum(targets  .* log( acts{end}) + (1 - targets) .* log( 1 - acts{end}), 2) .* weights);
    Ix = (acts{end} - targets) ./ n ;  % discrepancy between acts and targets (assumes linear output layer)

  case 'softMax'
    % Compute value of cost function (softmax error)
    if( ~strcmp(network{i}.hidtype, 'exp') )
      error('softMax rule only works for exp output units')
    end
    acts{end} = exp(acts{end});
    acts{end} = acts{end}./repmat(sum(acts{end},2),[1,size(acts{end},2)]);
    C = -sum(sum( targets(:,1:end).*log(acts{end}), 2) .* weights) ;
    Ix = (acts{end} - targets);  % discrepancy between acts and targets (max output layer)

  case 'linSquaredErr'
      if( ~strcmp(network{i}.hidtype, 'gaussian') )
        error('linSquaredErr rule only works for gaussian (i.e., linear) output units')
      end
      C = 0.5 * sum(sum( (acts{end}-targets).^2, 2 ) .* weights);
      Ix = (acts{end}-targets);
  end
  
  Ix = Ix .* repmat( weights, [1, size(Ix,2)] );
  % Compute gradients
  for i=numHiddenLayers:-1:1
    % It's easier to write if we augment activations with ones
    acts{i} = [acts{i} ones(n,1)];
     
    % Compute delta in next layer
    delta = acts{i}' * Ix;

    % split delta into weights and bias part
    dW{i} = delta(1:end - 1,:)';
    db{i} = delta(end,:)';

    % Backpropagate error
    if i > 1
      switch(network{i-1}.hidtype)
      case 'sigmoid'
        Ix = (Ix * [network{i}.W network{i}.bias]) .* acts{i} .* (1 - acts{i});
      case 'gaussian'
        Ix = Ix * [network{i}.W network{i}.bias];
      otherwise
        error('unknown hidden layer type.')
      end
      Ix = Ix(:,1:end - 1);
    end
  end

  % Convert gradient information
  dC = repmat(0, [numel(v) 1]);
  ind = 1;
  for i=1:numHiddenLayers
      dC(ind:ind - 1 + numel(dW{i})) = dW{i}(:); ind = ind + numel(dW{i});
      dC(ind:ind - 1 + numel(db{i})) = db{i}(:); ind = ind + numel(db{i});
  end


