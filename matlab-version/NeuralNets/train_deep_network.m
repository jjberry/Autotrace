function [network, trainerr, validerr, first_eta] = train_deep_network(X, layer_size, layer_type, finetune, targets, validationX, validationTargets, sample, max_iter_rbm, max_iter_finetune, weights)
%TRAIN_DEEP_NETWORK Trains a deep (multi-layer) network using RBMs
%
%   network = train_deep_network(X, layers, finetune)
%   network = train_deep_network(X, layers, 'Backprop', targets);
%   network = train_deep_network(X, {['gaussian' | 'sigmoid'], ... }, layers, finetune)
%   network = train_deep_network(X, {['gaussian' | 'sigmoid'], ... }, layers, 'Backprop', targets);
%
% The function trains a deep multi-layer feedforward network on the 
% data specified in X by training each layer separately using Restricted 
% Boltzmann Machine training. The depth and number of nodes in the network 
% are specified by the vector layers. For instance, if layers is set to 
% [n 100 50 10], a network is trained with three hidden layers with 
% respectively 100, 50 nodes and 10 nodes. The number of input (visual)
% nodes mus be the same as the dimensionality of the input data X. The
% network is trained using a greedy approach. The network may be finetuned
% using backpropagation or contrastive wake-sleep by setting finetune. 
% Possible values are 'Backprop', 'WakeSleep', or 'None' (default = 'None').
% The network is returned in the cell-array network.
%

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

    if ~exist('layer_size', 'var') || isempty(layer_size)
      layer_size = [20 10];
    end
    if (layer_size(1) ~= size(X,2))
      disp('Assuming that the visible layer was omitted from layer_size.')
      layer_size = [size(X,2), layer_size];
    end
    if ~exist('layer_type','var') || isempty(layer_type)
      layertype = cell(length(layer_size));
      [layertype{:}] = deal('sigmoid');
      layertype{end} = 'gaussian';
    end
    if ~exist('finetune', 'var') || isempty(finetune)
      finetune = 'None';
    end    
    if length(layer_size) ~= length(layer_type)
      error('length of layer_size and layer_type do not agree');
    end
    if ~exist('weights', 'var') || isempty(weights)
      weights = ones(size(X,1),1);
    end
    if ~exist('sample', 'var') || isempty(sample)
      sample = false;
    end
    
    disp(['Layer sizes: ', sprintf('%9d ', layer_size)]);
    disp(['Layer types: ', sprintf('%9.9s ', layer_type{:})]);
    disp(' ');
    
    if ~exist('max_iter_rbm', 'var') || isempty(max_iter_rbm)
        max_iter_rbm = 100;
    end
    if ~exist('max_iter_finetune', 'var') || isempty(max_iter_finetune)
        max_iter_finetune = 30;
    end

    % Initialize some variables
    no_hidden_layers = length(layer_size)-1;
    network = cell(1, no_hidden_layers);
    %X = X -  min(min(X));
    %X = X ./ max(max(X));
    origX = X;
    optimize_first_layer = true;
    % Learn layer-by-layer to get an initial network configuration
    for i=1:no_hidden_layers
      fprintf(1,['Training layer ' num2str(i)]);
      
      % Train current layer
      if i ~= no_hidden_layers || (i==1 && no_hidden_layers==1)
        if i == 1 && optimize_first_layer
          %etas = [0.0025, 0.001, 0.0001, 0.000025];
          etas = [0.001, 0.0001, 0.000025];
            for j = 1:length(etas)
                [networks{j} recon_error] = train_rbm(X, layer_size(i+1), layer_type{i}, layer_type{i+1}, etas(j), max_iter_rbm*5, sample, weights);
                recon_errors(j) = recon_error(2);
%                if j > 1 && ~(isinf(recon_errors(j)) || isnan(recon_errors(j)))...
%                         && ~(isinf(recon_errors(j-1)) || isnan(recon_errors(j-1)))
                 if ~(isinf(recon_errors(j)) || isnan(recon_errors(j)))
                     break;
                end
            end
            [val, ind] = min(recon_errors);
            first_eta = etas(ind)
            network{i} = networks{ind};
        else
            [network{i} recon_error] = train_rbm(X, layer_size(i+1), layer_type{i}, layer_type{i+1}, [], max_iter_rbm, sample, weights);
        end
        % Transform data using learned weights, so input to layer is the transformed data from previous layer
        % Warning: allways assumes sigmoidal hidden units. Not good.
        % X = 1 ./ (1 + exp(-(X * network{i}.W + repmat(network{i}.bias_upW, [size(X, 1) 1]))));
        n = network{i}; n.W = n.W'; n.bias = n.bias_upW';
        X = run_through_network({n}, X);
      else
        switch finetune
        case {'Autoencoder', 'Unsupervised', 'None'}
          network{i} = train_rbm(X, layer_size(i+1), layer_type{i}, layer_type{i+1}, [], max_iter_rbm, sample, weights);
        otherwise
          % just init top layer with random weights
          network{i}.W = randn([layer_size(i) layer_size(i+1)]) * 0.1;
          network{i}.bias_upW = zeros([1 layer_size(i+1)]);
          network{i}.bias_downW = zeros([1 layer_size(i)]);
          network{i}.vistype = layer_type{i};
          network{i}.hidtype = layer_type{i+1};
        end
      end
    end
    disp(' ');
    save network network

    % Perform finetuning if desired
    switch finetune
        
      %case 'WakeSleep'
        %disp('Finetuning the network using the contrastive wake-sleep algorithm...');
        %network = wake_sleep(network, origX); 
          
      case 'Autoencoder'
        disp('Finetuning the autoencoder using backpropagation...');
        no_layers = length(network);
        for i=1:no_layers
          network{2 * no_layers + 1 - i} = network{i};
          network{2 * no_layers + 1 - i}.bias = network{i}.bias_downW';
          network{2 * no_layers + 1 - i}.hidtype = network{i}.vistype;
          network{2 * no_layers + 1 - i}.vistype = network{i}.hidtype;          
          network{i}.W = network{i}.W';
          network{i}.bias = network{i}.bias_upW';
        end
        % network{no_layers + 1}.type = 'sigmoid';
        % [network, trainerr, validerr] = backprop(network, origX, origX, max_iter_finetune, 'crossEntropy', validationX, validationTargets, 'reconstruction', 0, weights);
        [network, trainerr, validerr] = backprop(network, origX, origX, max_iter_finetune, 'linSquaredErr', validationX, validationTargets, 'reconstruction', 0, weights);
        
      case 'Backprop'
        disp('Finetuning the network using backpropagation...');
        for i=1:length(network)
          network{i}.W = network{i}.W';
          network{i}.bias = network{i}.bias_upW';
        end
        [network, trainerr, validerr] = backprop(network, origX, targets, max_iter_finetune, 'softMax', validationX, validationTargets, 'classification', [], weights);
          
      case {'Unsupervised', 'None', 'Extern'}
        for i=1:length(network)
          network{i}.W = network{i}.W';
          network{i}.bias = network{i}.bias_upW';
        end
        trainerr = 0;
        validerr = 0;
      otherwise
          % Do nothing
    end
