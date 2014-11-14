function network = nonlinnca(data, layer_size, layer_type, targets, validationX, validationTargets)

  [network] = train_deep_network(data, layer_size, layer_type, 'Extern');

  no_layers = length(network);
  for i=1:no_layers
    network{2 * no_layers + 1 - i} = network{i};
    network{2 * no_layers + 1 - i}.bias = network{i}.bias_downW';
    network{2 * no_layers + 1 - i}.hidtype = network{i}.vistype;
    network{2 * no_layers + 1 - i}.vistype = network{i}.hidtype;          
    network{i}.W = network{i}.W';
    network{i}.bias = network{i}.bias_upW';
  end

  validErrFun = 'crossEntropy';

  % For estimating test error
  tindex = randperm(n);
  tinds = tindex(1:min([batch_size n]));
  
  % Perform the gradient descent procedure
  fprintf(1,['Starting ' num2str(max_iter) ' iterations of backprop.\n']);
  for iter=1:max_iter
    % Print progress
    [trainreconerr, trainclasserr] = getError(network, X(tinds,:), T(tinds,:), weights(tinds));
    if exist('validationX', 'var') && ~isempty(validationX)
      validclasserr = getError(network, validationX, validationTargets, weights(tinds), validErrFun);
      disp(sprintf('Iteration %3d: TrainErr = %4.3f, ValidErr = %4.3f', iter, trainclasserr, validclasserr));
    else
      disp(sprintf('Iteration %3d: TrainErr = %4.3f', iter, trainclasserr));
    end
    [network] = doBackprop(X, network, targets);
  end

  trainerr = getError(network, X(tinds,:), T(tinds,:), weights(tinds), validErrFun);
  if exist('validationX', 'var') && ~isempty(validationX)
    validerr = getError(network, validationX, validationTargets, weights(tinds), validErrFun);
    disp(sprintf('Final        : TrainErr = %4.3f, ValidErr = %4.3f', trainerr, validerr));
  else
    disp(sprintf('Final        : TrainErr = %4.3f', trainerr));
  end

  function [curnet] = doBackprop(traindata, curnet, targets)
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
  
      % Convert the weights and store them in a vector for 'minimize'
      v = [];
      for i=1:length(curnet)
          v = [v; curnet{i}.W(:); curnet{i}.bias(:)];
      end
  
      % Conjugate gradient minimization using 3 linesearches
      v = minimize(v, 'backprop_nca_gradient', 3, curnet, tmpX, tmpT, 'crossEntropy', tmpW);
  
      % Deconvert the weights and store them in the network
      ind = 1;
      for i=1:no_layers
          curnet{i}.W    = reshape(v(ind:ind - 1 + numel(curnet{i}.W)),    size(curnet{i}.W));     ind = ind + numel(curnet{i}.W);
          curnet{i}.bias = reshape(v(ind:ind - 1 + numel(curnet{i}.bias)), size(curnet{i}.bias));  ind = ind + numel(curnet{i}.bias);
      end
    end
  end
  
  function [reconerr, classerr] = getError(network, vX, vT, vW)
    classerr = 0;
    reconerr = 0;
    result = run_through_network(network, vX);
    for i = 1:size(vX,1)
        [val, ind] = max(result(i,:));
        if ind ~= find(vT(i,:))
          classerr = classerr + vW(i);
        end
        reconerr = reconerr + sqrt(sum( (result(i,:)-vT(i,:)).^2)) * vW(i) ;
    end
    classerr = classerr ./ size(vX,1);
    reconerr = reconerr ./ size(vX,1);
  end

end

