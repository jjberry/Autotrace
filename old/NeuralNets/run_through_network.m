function result = run_through_network(network, X,targetCost)
%RUN_THROUGH_NETWORK Runs a set of points through a neural network
%
%   result = run_through_network(network, X)
%
% The function runs a set of points through a neural network that was
% trained by the TRAIN_DEEP_NETWORK function using either the 'Backprop' or
% 'Autoencoder' setting.
%
%
% (C) Laurens van der Maaten
% Maastricht University, 2007
%

    if nargin < 3
        targetCost = 'linSquaredError';
    end

    % Run through network
    no_layers = length(network) + 1;
    activations = X;
    for i=1:no_layers - 1
        if strcmp(network{i}.hidtype, 'sigmoid')
            activations =  1 ./ (1 + exp(-(activations * network{i}.W' + repmat(network{i}.bias', [size(X, 1) 1]))));
        else
            activations = activations * network{i}.W' + repmat(network{i}.bias', [size(X, 1) 1]);
        end
    end
    result = activations;

    if strcmp(targetCost,'softMax')
        result = exp(result);
        result = result./repmat(sum(result,2),[1,size(result,2)]);
    end

