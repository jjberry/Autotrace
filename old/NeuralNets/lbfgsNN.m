function [network, trainerr, validerr] = lbfgsNN(network, X, T, max_iter, targetCost, ...
                                                  validationX, validationTargets, ...
                                                  validErrFun, initialfit, weights)
% lbfgs on network using dataset X and targets T  

  n = size(X,1);
  if ~exist('max_iter', 'var') || isempty(max_iter)
      max_iter = 1000;
  end
  if ~exist('validErrFun', 'var') || isempty(validErrFun)
      validErrFun = 'linSquaredErr';
  end
  if ~exist('weights', 'var') || isempty(weights)
      weights = ones(n,1);
  end

  % Convert the weights and store them in the network
  v = [];
  for i=1:length(network)
      v = [v; network{i}.W(:); network{i}.bias(:)];
  end

  fn = @bp_short
  function [C, dC] = bp_short(v)
    [C, dC] = backprop_gradient(v, network, X, T, targetCost, weights);
  end
  
  opts = lbfgs_options('iprint', -1, 'maxits', max_iter, 'factr', 1e5, ...
                       'cb', @test_callback);
  [v,trainerr,exitflag,userdata] = lbfgs(fn,v,opts);
  
  % Deconvert the weights and store them in the network
  ind = 1;
  no_layers = length(network);
  for i=1:no_layers
      network{i}.W    = reshape(v(ind:ind - 1 + numel(network{i}.W)),    size(network{i}.W));     ind = ind + numel(network{i}.W);
      network{i}.bias = reshape(v(ind:ind - 1 + numel(network{i}.bias)), size(network{i}.bias));  ind = ind + numel(network{i}.bias);
  end
  
  if exist('validationX', 'var') && ~isempty(validationX)
    validerr = getError(network, validationX, validationTargets, ones(size(validationX,1),1), validErrFun);
    disp(sprintf('Final        : TrainErr = %4.3f, ValidErr = %4.3f', trainerr, validerr));
  else
    disp(sprintf('Final        : TrainErr = %4.3f', trainerr));
  end


  function validerr = getError(network, vX, vT, vW, validErrFun)
    err = 0;
    result = run_through_network(network, vX);
    for i = 1:size(vX,1)
      if strcmp(validErrFun, 'classification')
        [val, ind] = max(result(i,:));
        if ind ~= find(vT(i,:))
          err = err + vW(i);
        end
      else
        err = err + sqrt(sum( (result(i,:)-vT(i,:)).^2)) * vW(i) ;
      end
    end
    validerr = err ./ size(vX,1);
  end
  
end