function [data, nnet] = normalizedata(data, nnet, method, varargin)

    switch(method)
    case 'pca'
        percent_var = varargin{1};
    case 'scale'
        scale = varargin{1};
    end
    
    if nargin < 3
        if nargin == 2 && isstruct(nnet) && isfield(nnet,'normalization_type')
            method = nnet.normalization_type;
        else
            method = 'mean_and_var';
            nnet.normalization_type = method;
        end
    end
    
    switch(method)
    case 'none'
        % do nothing

    case 'zero_one'  % linearly scale each var so min and max map to between zero and one
        for i = 1:size(data,2)
            nnet.min(i) = min(data(:,i));
            data(:,i) = data(:,i) - nnet.min(i);
            nnet.max(i) = max(data(:,i));
            data(:,i) = data(:,i) ./ nnet.max(i);
        end

    case 'scale'
      for i = 1:size(data,2)
        nnet.mean(i) = 0;
        nnet.std(i) = scale(i);
        data(:,i) = data(:,i)./scale(i);
      end
    case 'mean_and_var'
        % Simply normalize mean and var of each variable independently
        for i = 1:size(data,2)
            nnet.mean(i) = mean(data(:,i));
            data(:,i) = data(:,i) - nnet.mean(i);
            nnet.std(i) = std(data(:,i));
            data(:,i) = data(:,i) ./ nnet.std(i);
        end

    case 'pca'
        % Use PCA to capture top percent_var of the variance
        
        % zero mean
        nnet.mean = mean(data,1);
        data = data - repmat(nnet.mean, [size(data, 1) 1]);
        
        % Compute covariance matrix
        C = cov(data);
        
        % Perform eigendecomposition of C
        C(logical( isnan(C) | isinf(C) )) = 0;
        [M, lambda] = eig(C);
        
        % Sort eigenvectors in descending order
        [lambda, ind] = sort(diag(lambda), 'descend');
        M = M(:,ind);
        
        % maybe remove some noise, but you can keep original dimensionality too, just make this a parameter
        if percent_var < 1
            ind = min(find(cumsum(lambda)./sum(lambda) >= percent_var));
            if ~isempty(ind)
                M = M(:,1:ind);
                lambda = lambda(1:ind);
            end
            if ind < size(data,2)
                warning(['normalizing data with PCA based pre-whitening has reduced the dimensionality of the data to ', num2str(ind) ]);
            end
        end
        % Project data onto principal axes
        data = data * (M * diag(1./sqrt(lambda)));
        
        % store params so we can transform new data
        nnet.M = M;
        nnet.lambda = lambda;

    end

