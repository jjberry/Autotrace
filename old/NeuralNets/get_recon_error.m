function [reconerr, angle_reconerr, result] = get_recon_error(nnet, data)
    result = normed_run_through_network(nnet, data);

    err = 0;
    angle_err = 0;
    for i = 1:size(result,1)
      % add two kinds of distances
      err = err + sqrt(sum( (result(i,:) - data(i,:)).^2 ));
      angle_err = angle_err + acos((result(i,:) * data(i,:)') ./ (norm(result(i,:)) * norm(data(i,:))));
    end

    % divid by number of samples
    reconerr = err ./ size(result,1);
    angle_reconerr = angle_err ./ size(result, 1);
