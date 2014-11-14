function reconresult = normed_run_through_network(nnet, data)
    reconresult = zeros(size(data));
    if isfield(nnet, 'normalization_type')
        switch(nnet.normalization_type)
        case 'none'
            % do nothing
        case 'zero_one'
            for i = 1:size(data,2)
                data(:,i) = data(:,i) - nnet.min(i);
                data(:,i) = data(:,i) ./ nnet.max(i);
            end
        case 'mean_and_var'
            for i = 1:size(data,2)
                data(:,i) = data(:,i) - nnet.mean(i);
                data(:,i) = data(:,i) ./ nnet.std(i);
            end
        case 'pca'
            data = data - repmat(nnet.mean, [size(data, 1) 1]);
    	    data = data * (nnet.M * diag(1./sqrt(nnet.lambda)));
        end
    end
    
    if length(nnet.network) > 0
        result = run_through_network(nnet.network, data);
    else
        result = data;
    end
    
    % unnorm the reconstruction
    if isfield(nnet, 'normalization_type')
        switch(nnet.normalization_type)
        case 'none'
            reconresult = result;
        case 'zero_one'
            for i = 1:size(result,2)
                reconresult(:,i) = result(:,i) .* nnet.max(i) + nnet.min(i);
            end
        case 'mean_and_var'
            for i = 1:size(result,2)
                reconresult(:,i) = result(:,i) .* nnet.std(i) + nnet.mean(i);
            end
        case 'pca'
            for i = 1:size(result,1)
        	    reconresult(i,:) = nnet.M * (result(i,:)' .* sqrt(nnet.lambda)) + nnet.mean';
            end
        end
    end

    