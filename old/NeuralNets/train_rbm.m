function [machine, recon_err] = train_rbm(X, h, vistype, hidtype, eta, max_iter, sample, weights)
%TRAIN_RBM Trains a Restricted Boltzmann Machine using contrastive divergence
%
%   machine = train_rbm(X, h, vistype, hidtype, eta, max_iter)
%
% Trains a first-order Restricted Boltzmann Machine on dataset X. The RBM
% has h hidden nodes (default = 20). The training is performed by means of
% the contrastive divergence algorithm. The activation function that
% is applied in the hidden layer is specified by type. Possible values are
% 'linear' and 'sigmoid' (default = 'sigmoid'). In the training of the RBM,
% the learning rate is determined by eta (default = 0.25). The maximum 
% number of iterations can be specified through max_iter (default = 50). 
% The trained RBM is returned in the machine struct.
%
% A Boltzmann Machine is a graphical model which in which every node is
% connected to all other nodes, except to itself. The nodes are binary,
% i.e., they have either value -1 or 1. The model is similar to Hopfield
% networks, except for that its nodes are stochastic, using a logistic
% distribution. It can be shown that the Boltzmann Machine can be trained by
% means of an extremely simple update rule. However, training is in
% practice not feasible.
%
% In a Restricted Boltzmann Machine, the nodes are separated into visible
% and hidden nodes. The visible nodes are not connected to each other, and
% neither are the hidden nodes. When training an RBM, the same update rule
% can be used, however, the data is now clamped onto the visible nodes.
% This training procedure is called contrastive divergence. Alternatively, 
% the visible nodes may be Gaussians instead of binary logistic nodes.
%


    % Process inputs
    if ~exist('h', 'var') || isempty(h)
        h = 20;
    end
    if ~exist('hidtype', 'var') || isempty(hidtype)
        hidtype = 'sigmoid';
    end
    if ~exist('vistype', 'var') || isempty(vistype)
        vistype = 'sigmoid';
    end
    if ~exist('max_iter', 'var') || isempty(max_iter)
        max_iter = 100;
    end
    if ~exist('weights', 'var') || isempty(weights)
      weights = ones(size(X,1),1);
    end
    if ~exist('eta', 'var') || isempty(eta)
      if any(strcmp('gaussian', {vistype, hidtype}))
        eta = 0.1;
      else
        eta = 0.1;
      end
    end
    disp([', visible layer: ', vistype, ', hidden layer: ', hidtype, '.']);

    % Experimental: rather than sample, just use prob
    if ~exist('sample','var')
        sample = true;
    end
    
    % Important parameters
    initial_momentum = 0.5;     % momentum for first five iterations
    final_momentum = 0.9;       % momentum for remaining iterations
    weight_cost = 0.0002;       % costs of weight update
    
    momentum_iter = 5;
    %momentum_iter = 20;
    
    % Initialize some variables
    [n, v] = size(X);
    batch_size = max([1000,1 + round(n / 20)]);    
    W = randn(v, h) * 0.1;
    bias_upW = zeros(1, h);
    bias_downW = zeros(1, v);
    deltaW = zeros(v, h);
    deltaBias_upW = zeros(1, h);
    deltaBias_downW = zeros(1, v);
    
    recon_err = [0, 0];
    
    % Main loop
    for iter=1:max_iter
      errsum=0;
      
      % Print progress
      if rem(iter, 10) == 0
          disp(['Epoch ' num2str(iter)]);
      end
      
      % Set momentum
      if iter <= momentum_iter
          momentum = initial_momentum;
      else
          momentum = final_momentum;
      end
      
      % Run for all mini-batches (= Gibbs sampling step 0)
      ind = randperm(n);
      for batch=1:batch_size:n
        batchind = ind(batch:min([batch + batch_size - 1 n]));
        numpoints = length(batchind);
        
        % Set values of visible nodes (= Gibbs sampling step 0)
        vis1 = double(X(batchind,:));

        if (sample)
            % Compute probabilities for hidden nodes (= Gibbs sampling step 0)
            [hid1, hid1state] = sampleOtherLayer(hidtype, vis1, W, bias_upW);
            % Compute probabilities for visible nodes (= Gibbs sampling step 1)
            vis2 = sampleOtherLayer(vistype, hid1state, W', bias_downW);
        else
            % Compute probabilities for hidden nodes (= Gibbs sampling step 0)
            hid1 = sampleOtherLayer(hidtype, vis1, W, bias_upW);
            % Compute probabilities for visible nodes (= Gibbs sampling step 1)
            vis2 = sampleOtherLayer(vistype, hid1, W', bias_downW);        
        end
        
        % Compute probabilities for hidden nodes (= Gibbs sampling step 1)
        hid2 = sampleOtherLayer(hidtype, vis2, W, bias_upW);

        % Now compute the weights update (= contrastive divergence)
        posprods = hid1' * (vis1 .* repmat( weights(batchind,:), [1, size(vis1,2)]));
        negprods = hid2' * (vis2 .* repmat( weights(batchind,:), [1, size(vis2,2)]));

        err= sum( (vis1-vis2).^2, 2 )' * weights(batchind,:);
        errsum = err + errsum;

        deltaW = momentum * deltaW + (eta / numpoints) * ((posprods - negprods)' - (weight_cost * W));
        deltaBias_upW   = momentum * deltaBias_upW   + (eta / numpoints) * (sum(hid1, 1) - sum(hid2, 1));
        deltaBias_downW = momentum * deltaBias_downW + (eta / numpoints) * (sum(vis1, 1) - sum(vis2, 1));

        % Divide by number of elements for linear activations
        % if strcmp(hidtype, 'gaussian') || strcmp(vistype, 'gaussian') 
        %     deltaW = deltaW                   ./ 30; %numel(deltaW);
        %     deltaBias_upW = deltaBias_upW     ./ 30; %numel(deltaBias_upW);
        %     deltaBias_downW = deltaBias_downW ./ 30; %numel(deltaBias_downW);
        % end
        
        % Update the network weights
        W           = W          + deltaW;
        bias_upW    = bias_upW   + deltaBias_upW;
        bias_downW  = bias_downW + deltaBias_downW;
      end
      if(iter==1)
        recon_err(:) = errsum ./ (n * v);
        disp(['Reconstruction error = ', num2str( recon_err(1) )]);
      elseif rem(iter, 10) == 0
        recon_err(2) = errsum ./ (n * v);
        disp(['Reconstruction error = ', num2str( recon_err(2) )]);
      end
      err_history(iter) = errsum ./ (n * v);
      if any(isnan(recon_err)) || any(isinf(recon_err)) || mean(recon_err) > 1000
        break;
      end
      if(iter > 250) && (mean(err_history(iter-50:iter)) * 1.2  > mean(err_history(iter-200:iter-150)))
          break;
      end
      % if(any(strcmp('gaussian', {vistype, hidtype})))
      %   if(iter==1)
      %       initial_err = errsum ./ (n * v);
      %   else
      %       if (errsum ./ (n * v) < 0.01 * initial_err)
      %           break;
      %       end
      %   end
      % end
    end
    % keyboard
    %   imshowtrue(reshape(vis1(10,:),[28,28])')
    %   imshowtrue(reshape(vis2(10,:),[28,28])')

    % Return RBM
    machine.W = W;
    machine.bias_upW = bias_upW;
    machine.bias_downW = bias_downW;
    machine.hidtype = hidtype;
    machine.vistype = vistype;

    machine.tied = 'yes';
    disp(' ');

    function [outprob, outstate] = sampleOtherLayer(type, indata, Wts, mybias)
      % Compute probabilities for hidden nodes (= Gibbs sampling step 0)
      switch type
      case 'sigmoid'
        outprob = 1 ./ (1 + exp(-(indata * Wts + repmat(mybias, [numpoints 1]))));
      case 'gaussian'
        outprob = indata * Wts + repmat(mybias, [numpoints 1]);
      end

      % Maybe draw sample instead of sending expectations....
      if (nargout > 1)
        switch type
        case 'sigmoid'
          outstate = outprob > rand(size(outprob));
        case 'gaussian'
          outstate = outprob + randn(size(outprob));
        end
      else
        outstate = [];
      end
    end

end
